from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
from django.views import View 
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model 
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout
from django.template import loader
from .models import user_datails

User=get_user_model()
#user register and activate 
class Registration(APIView):
    def post(self,request):
        spl=['@','#','$','%','&','^','_','*']
        #email validation 
        if 'email' not in request.data:
            return Response({"status":"empty email"})
        if request.data["email"] == '':
            return Response({"status":"fill email"})
        if User.objects.filter(email=request.data["email"].strip()).exists():
            return Response({"status":"email is allready exist"})

        #firstname validation
        if 'first_name' not in request.data:
            return Response({"status":"empty firstname"})
        if request.data["first_name"].strip() == '':
            return Response({"status":"fill first_name"})
        for i in request.data['first_name']:
            if i in spl:
                return Response({"status":"fail","msg":"lastname can not contain special character"})
            if i.isdigit():
                return Response({"status":"fail","msg":"lastname can not digit name"}) 

        if request.data["password"].strip() =='':
            return Response({"status":"fill password"})

        # #lastname validation
        if 'last_name' not in request.data:
            return Response({"status":"empty firstname"})
        
        if request.data["last_name"].strip() =='':
            return Response({"status":"fill last_name"})

        for i in request.data['last_name']:
            if i in spl:
                return Response({"status":"fail","msg":"lastname can not contain special character"})
            if i.isdigit():
                return Response({"status":"fail","msg":"lastname can not digit name"}) 

        if request.data["password"].strip() =='':
            return Response({"status":"fill password"})



        #password validation
        l, u, p, d = 0, 0, 0, 0
        if 'password' not in request.data:
            return Response({"status":"fail","msg":"please enter the password"})

        if request.data['password']== "":
            return Response({"status":"fail","msg":"password fiels must be fillup"})

        if (len(request.data['password']) >= 8):
            for i in request.data['password']:
                if i.isupper():
                    l+=1
                elif i.islower():
                        u+=1
                elif i.isdigit():
                        p+=1
                elif i in spl:
                        d+=1

        else:
            #"Password Must Be More Then 8 Character Long..."
            return Response({"status":"fail","msg":"Password Must Be More Then 8 Character Long"})
        
        if request.data["password"].strip() =='':
            return Response({"status":"fill password"})

        if len(request.data["password"]) < 8:
            return Response({'status': 'fail', 'message': 'Password must be at least 8 characters long.'})
        user = User.objects.create_user(email=request.data["email"].strip(),password=request.data["password"],first_name=request.data["first_name"],
                            last_name=request.data["last_name"])
        a=user_datails.objects.create(user_id=user, dob=request.data["dob"],bio=request.data["bio"])
        
        token=Token.objects.get_or_create(user=user)
        token = " ".join([str(x) for x in token]).replace("True",'').strip()
        user.is_active=False 
        user.save()

        email_body='http://127.0.0.1:8000/registration/'+token
        email_subject='Activate your Account',
        html_message = loader.render_to_string(
                '/home/sipl/Downloads/api/crud_api_class_based/crudClassBased/templates/activation.html',
                {
                    'user_name': user.first_name,
                    'emailbody':  email_body
                    
                }
            )
        #send mail to activate account
        send_mail(
        email_subject,
        email_body,
        'test.softude@gmail.com',
        [request.data["email"]],
        html_message=html_message,
        fail_silently=False,
        )
        return Response({"status":"all set",'message':"go to the your emailid and click on the activation link to confirm"})


    def get(self,request,token):
        try:
            tokens = Token.objects.get(key = token)
            user=tokens.user 
            if user:
                user.is_active = True
                user.save()
                login(request, user)
                Token.objects.filter(key = token).delete()
                return Response({"status":"all set",'message':"activated"})
            else:
                return Response({"status":"fail",'message':"activation failed"})
        except:
            return Response({"status":"fail",'message':"token is invalid"})
#user login and logout
class user_login(APIView):
    def post(self,request):
        try:
            #email validation 
            if 'email' not in request.data:
                return Response({"status":"empty email"})
            if request.data["email"] == '':
                return Response({"status":"fill email"})
            if 'password' not in request.data:
                return Response({"status":"empty password"})            
            if request.data["password"].strip() =='':
                return Response({"status":"fill password"})

            u_email=request.data["email"].strip()
            u_password=request.data["password"].strip()
            user=authenticate( email=u_email , password = u_password )
            if user:    
                login(request, user)
                token=Token.objects.get_or_create(user=user)
                return Response({
                    'status':'success',
                    'massage':'login succesfully',
                    'token':str(token)   
                })
            else:
                return Response({
                    'status':'fail',
                    'message':"invalid credentials"
                })
        except Exception:
            return Response({
                'status':'fail',
                'message':"something went wrong"
            })
        
    #logout user        
    def get(self,request):
        try:
            user_token=request.headers["Authorization"]
            token=Token.objects.get(key=user_token)
            user=token.user
            uid=token.user_id
            logout(request)
            token.delete()
            return Response({"status":"succcess","message":"logout succesfull"})
        except:
            return Response({'status': 'fail', 'message': 'token is invalid.'})       


#get_data,update_data_put,update_data_patch,delete_data
class CrudData(APIView):
    def get(self,request):  
        try:
            token=Token.objects.get(key=request.headers["Authorization"])
            user=token.user
            uid=token.user_id
            
            if user:
                userd=User.objects.filter(id=uid).values("id","email","first_name","last_name")
                user_data=user_datails.objects.filter(user_id=userd[0]["id"]).values("dob","bio")
                data=userd[0]
                for i,j in user_data[0].items():
                    data[i]=j
                return Response({
                        'status':'success',
                        'massage':"all data" ,'data':userd  
                    })
            return Response({
                'status':'fail',
                'message':"this user is not available"
            })
            
        except:
            return Response({
                'status':'fail',
                'message':"your token is wrong"
            })


    #update_data
    def put(self,request):
        try:
            token=Token.objects.get(key=request.headers["Authorization"])
            user=token.user
            print(user)
            uid=token.user_id
            print(uid)
        
            #firstname validation
            if 'first_name' not in request.data:
                return Response({"status":"fail","message":"empty firstname"})
            if request.data["first_name"].strip() == '':
                return Response({"status":"fail","message":"fill first_name"})

            #lastname validation
            if 'last_name' not in request.data:
                return Response({"status":"fail","message":"empty firstname"})
            if request.data["last_name"].strip()=='':
                return Response({"status":"message","message":"fill last_name"})
        
            #dob validation
            if 'dob' not in request.data:
                return Response({"status":"fail","message":"empty dob"})
            if request.data["dob"].strip()=='':
                return Response({"status":"fail","message":"fill dob"})

            #bio validation
            if 'bio' not in request.data:
                return Response({"status":"fail","message":"empty bio"})
            if request.data["bio"].strip()=='':
                return Response({"status":"fail","message":"fill bio"})

            User.objects.filter(id=uid).update(first_name=request.data["first_name"],last_name=request.data["last_name"])
            user_datails.objects.filter(user_id=uid).update(bio=request.data["bio"],dob=request.data["dob"])
            return Response({"status":"success","message":"update successfully"})
        except:
            return Response({"status":"fail","message":"this id/token is not valid"})
    
    #update partially user data
    def patch(self,request):
        try:
            token=Token.objects.get(key=request.headers["Authorization"])
            user=token.user
            uid=token.user_id

            myDict = dict(request.data.lists())
            data={}
            userdata={}
            user_dataildata={}
            for i,j in myDict.items():  
                data.update({i:j[0]})
        
            if "bio" in data:
                userdata["bio"]=request.data["bio"]
            if "first_name" in data:
                user_dataildata["first_name"]=request.data["first_name"]
            if "last_name" in data:
                user_dataildata["last_name"]=request.data["last_name"]
            if "dob" in data:
                userdata["dob"]=request.data["dob"]
            if "email" in data:
                user_dataildata["email"]=request.data["email"]     
            user_datails.objects.filter(user_id=uid).update(**userdata)
            User.objects.filter(id=uid).update(**user_dataildata)
            return Response({"status":"success","message":"update successfully"})
        except:
            return Response({'status': 'fail', 'message': 'token is invalid.'})
        
        
        
        
    #delete user data
    def delete(self,request):
        try:
            token=Token.objects.get(key=request.headers["Authorization"])
            user=token.user
            uid=token.user_id
            
            user=User.objects.get(id=uid)
            user_datails.objects.filter(user_id=user).delete()
            user.delete()
            return Response({"status":"success","message":"delete successfully","data":f"user id {uid} and {user.email} has deleted"})    
        except:
            return Response({"status":"fail","message":"this id is not available"})
        
        





class Reset_pass(APIView):
    def get(self,request):
        email=request.data["email"]
        user=User.objects.get(email=email)
        print(user)
        user_datails.objects.get(user_id=user)
        token=Token.objects.get_or_create(user=user)
        print(token)
        token = " ".join([str(x) for x in token]).replace("True",'').strip()
        email_body='http://127.0.0.1:8000/forget_password/'+token
        email_subject='Forget your password',

        #send mail to activate account
        send_mail(
        email_subject,
        email_body,
        'test.softude@gmail.com',
        [request.data["email"]],
        fail_silently=False,
        )
        return Response({"status":"success","message":"sent link to your gmail id","token":token})
    
    
    #forget_pass
    def post(self,request):
        try:
            token=Token.objects.get(key = request.headers["Authorization"])
            user1=token.user
            if request.headers["Authorization"]:
                new_password = request.data['new_password']
                confirm_password = request.data['confirm_password']
                first_isalpha = new_password[0].isalpha()
                if user1.check_password(new_password):
                    return Response({'status': 'fail', 'message': 'sorry can"t updeted because your old pass_word and new_password are  same'}) 
                if new_password != confirm_password:
                    return Response({'status': 'fail', 'message': 'New password and confirm password are not matched.'})
                if all(i.isalpha() == first_isalpha for i in new_password):
                        return Response({'status': 'fail', 'message': 'Password must be a combination of characters with '
                                                                    'numbers or special characters.'})
                if len(new_password) < 8:
                        return Response({'status': 'fail', 'message': 'Password must be at least 8 characters long.'})
                user=User.objects.get(email=user1)
                user.set_password(new_password)
                user.save()
                token.delete()
                return Response({'status': 'success', 'message': 'Password updated successfully'})
            return Response({'status': 'fail', 'message': 'old password did not match.'})
        except:
            return Response({'status': 'fail', 'message': 'token is invalid.'})








