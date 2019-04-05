# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework.response import Response
from django.core import serializers
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext
from rest_framework.views import APIView

#---------------------------------- Registration API -------------------------------------

class RegisterUser(APIView):
    """
    Register User 
        :supports simple registration

            first_name             :       First Name of User\n
            last_name              :       Last Name of User\n
            job                    :       Job\n
            company                :       company\n
            address1               :       Address Line 1 \n
            address2               :       Address Line 2 \n
            city                   :       City \n
            subscription           :       Kemgo News ('0','OFF'), ('1',"ON"))\n
            state                  :       State \n
            zipcode                :       zipcode \n
            country                :       country \n
            website                :       website \n
            office_number          :       Office Number \n
            useraccess             :       Multiple UserType [comma separated]
            mobile_number          :       Mobile Number \n
            language               :       Language Code    [Default : en]
    """
    # @csrf_exempt
    # def dispatch(self, *args, **kwargs):
    #     return super(RegisterUser, self).dispatch(*args, **kwargs)
    
    
    def get(self, request, format=None):
        # return MethodNotAllowed('GET')
         return Response({'Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        
    """
            variable used
                email : user email
                user_status : flag used for check user existence default False
                userdetail_obj : Object used for fetch exist email
     """
    def post(self, request, format=None): 
        if "language" in request.DATA : 
            langcode = request.DATA['language']
        else :
            langcode = 'en'    

        translation.activate(langcode)

        try :
            email = request.DATA["email"]
            fname = request.DATA["first_name"]
            lname = request.DATA["last_name"]
            mobilenumber = request.DATA["mobile_number"]
            # Check if email is already present 
            # check status of user (Active,blocked,deleted)
            # Delete inactive user then save user information.       
            is_activeuser=False
            try :                       
                userObj = User.objects.get(email = email)

                # check User Status  
                if (userObj.is_active != True):
                    try :
                        usercodeObj=CodeVerify.objects.get(user_id = userObj.id, source='register')
                        usercodeObj.delete()                                       
                        userObj.delete()
                        is_activeuser=True 
                    except Exception as e:
                        return Response(responsejson('Your Account is inactive state Please contact to Admin for more assistance', status=404))

                # check whether the user account is blocked
                if (userObj.is_block == '1'):
                    return Response(responsejson("Your Account has been Cancelled", status=404))

                # check whether the user account is deleted 
                if (userObj.is_delete == '1'):
                    baseurl=getbaseurl()
                    return Response(responsejson('This email is already registered with KEMGO. Please use a different email address or <a href="help/contactus"> contact us</a> for further assistance.', status=404))

                if (is_activeuser== False) :  
                    return Response(responsejson('This email is already registered with KEMGO. Please use a different email address or <a href="help/contactus"> contact us</a> for further assistance.', status=404))
            except :
                pass

            # Validate User and register 
            post_mutable = request.DATA.copy()
            # Now you can change values:
            post_mutable['membership'] = 0
            post_mutable['username'] =getUsername(fname + lname)
            user_serializer = UserSerializer(data=post_mutable)
            user_profile_serializer = UserProfileSerializer(data=post_mutable)
            if (user_serializer.is_valid() and user_profile_serializer.is_valid()):

                hashed_password, salt = hash_password(user_serializer.object.password) # generate salt and hashed_password
                api_key = generateapikey()

                # Save API key
                user_serializer.object.apikey = api_key                    

                # Save Hashed Password
                user_serializer.object.password = hashed_password
                user_serializer.save() # save user data
                
                fullname=fname + ' ' + lname
                user_profile_serializer.object.name =  fullname
                userNewObj= User.objects.latest('id') # get last inserted id of user
                const_factor = 111111
                user_profile_serializer.object.customuserid = "KEM-" + str( const_factor + int(userNewObj.id) )
                user_profile_serializer.object.user = userNewObj # assign user_id to user_profile
                user_profile_serializer.save() # save user profile
                #for save mobile number in smsvarify table
                Smsverify = SmsVerify(phonenumber=mobilenumber, status=0,user_id=userNewObj.id)
                #save mobile number in smsvarify table
                Smsverify.save()

                # generate activation code for user, insert it into db and send email
                code = random_generator()
                code_verify = CodeVerify(user_id = userNewObj.id, code = code, source='register')
                code_verify.save() # need some kind to exception handling
                baseurl=getbaseurl()
                finalurl= baseurl + "site/activate/code/" + str(code)+"||"+str(userNewObj.id)

                try :
                    if 'useraccess' in request.DATA:
                        access = request.DATA['useraccess']
                        obj = [e.encode('utf-8') for e in access.split(',')]
                        dataObj = []
                        for data in obj :
                            dataObj.append(UserAccess(user_id=userNewObj.id,usertype_id=data))
                        UserAccess.objects.bulk_create(dataObj)        
                except :
                    pass  
 
                try :
                    # send activati1on code in email
                    emailtemplate = Pages.objects.get(caption='template_of_user_registration',langcode=langcode)
                    content = emailtemplate.content
                    subject = emailtemplate.subject
                    content = content.replace("##URL##","<a href='"+finalurl+"''>"+finalurl+"</a>")
                    content = content.replace("##USER##",user_profile_serializer.object.name)

                    sendemail(user_serializer.object.email,subject,content,'kemgo.info@gmail.com')

                    # send mail to Admin 
                    emailtemplate = Pages.objects.get(caption='template_of_registration_admin',langcode=langcode)
                    content = emailtemplate.content
                    subject = emailtemplate.subject
                    content = content.replace("##EMAIL##",user_serializer.object.email)
                    sendemail('sumants@clavax.com',subject,content,user_serializer.object.email)
                except :
                    pass    

                return Response(responsejson(dict(user_serializer.data.items() + user_profile_serializer.data.items()), status=status.HTTP_201_CREATED) )
            else :
                return Response(responsejson(dict(user_serializer.errors.items() + user_profile_serializer.errors.items()),status=status.HTTP_400_BAD_REQUEST) )    
        except Exception as e:
            print e
            logger.error('Something went wrong!'+e.message)
            return Response(responsejson("There was an error in your request "+str(e.message), status=404))        
            


# Create your views here.
class UserLogin(APIView):
    """
        Login user in the system. \n
            email         --  email used when registering. \n
            password      --  password used when registering.
            language      --  language Code    [Default : en]
    """
    
    def post(self, request, format=None):
        try :
            langcode = request.DATA['language']
            translation.activate(langcode)
            if "email" in request.DATA and "password" in request.DATA:
                email = request.DATA["email"]
                password = request.DATA["password"]
                try:
                    u = User.objects.get(email=email)
                    
                    if (u.is_active == False):
                        
                        try :
                            CodeVerify.objects.get(user_id=u.id,source='register')    
                            return Response(responsejson("Please activate your account.", status=422))                
                        except :
                            return Response(responsejson("You are not active user, Please contact to Administrator ", status=422))


                    if verify_password(password, u.password):
                        try:
                            # check whether the user is blocked
                            if (u.is_block == '1'):
                                return Response(responsejson("Your Account has been Cancelled", status=404))
                            # check whether the user account is deleted 
                            if (u.is_delete == '1'):
                                return Response(responsejson("Your Account has been deleted by Admin", status=404))

                        except Exception as e:
                            return Response(responsejson("There was an error in your request", status=404))
                        #api_key = generateapikey()                     
                        #u.is_block = 0 

                        '''
                            Check OTP Code
                        '''
                        if "otp" in request.DATA:
                            if request.DATA["otp"] == "":
                                return Response(responsejson("Please enter correct otp code", status=404)) 
                            if (u.otpcode!=request.DATA["otp"]):
                               return Response(responsejson("Please enter correct otp code", status=404)) 
                        else :       
                            if u.securelogin == "1":
                                #send sms
                                sendOTP(u.id)
                                return Response(responsejson("Secure Login", status=200))
                        u.otpcode = ''        
                        u.last_login = timezone.now()
                        try :
                            u.ip = request.META['HTTP_X_FORWARDED_FOR']
                        except :      
                            u.ip = request.META['REMOTE_ADDR']

                        u.save()    
                        setting_str = []
                        for arr in u.usersetting_id.all():
                            sestr = {}
                            sestr['mobile'] = arr.mobile_setting
                            sestr['email'] = arr.email_setting
                            setting_str.append(sestr)

                        serializer = UserSerializer(u)
                        
                        up = UserProfile.objects.get(user=u)
                        serializer1 = UserProfileSerializer(up)
                        return Response(responsejson(dict(serializer.data.items() + serializer1.data.items() + setting_str), status=status.HTTP_201_CREATED))
                    else:
                        return Response(responsejson("Your email address or password is incorrect.", status=404))
                except User.DoesNotExist:
                    return Response(responsejson('You are not registered User ', status=404))
            else:
                return Response(responsejson("There was an error in your request", status=404))
        except Exception as e :
            print e
            return Response(responsejson("There was an error in your request" + str(e.message), status=404))    
