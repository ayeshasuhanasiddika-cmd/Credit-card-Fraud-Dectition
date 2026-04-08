from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth.models import User,auth 
from django.contrib import messages
from .models import Credit_Card
# Create your views here.
def index(request):
    return render(request,"index.html")


def adminlogin(request):
    if request.method=="POST":
        un=request.POST['uname']
        ps=request.POST['psw']
        user=auth.authenticate(username=un,password=ps)
        if user.is_superuser is not None:
            auth.login(request,user)
            return HttpResponseRedirect('adminhome')
        else:
            messages.info(request,"Invalid Credentials")
            return render(request,"adminlogin.html")
    return render(request,"adminlogin.html")

def register(request):
    if request.method=="POST":
        first=request.POST['fname']
        last=request.POST['lname']
        uname=request.POST['uname']
        em=request.POST['email']
        ps=request.POST['psw']
        ps1=request.POST['psw1']
        if ps==ps1:
            if User.objects.filter(username=uname).exists():
                messages.info(request,"Username Exists")
                return render(request,"register.html")
            elif User.objects.filter(email=em).exists():
                messages.info(request,"Email exists")
                return render(request,"register.html")
            else:
                user=User.objects.create_user(first_name=first,
            last_name=last,username=uname,email=em,password=ps)
                user.save()
                return HttpResponseRedirect("login")
        else:
            messages.info(request,"Password not Matching")
            return render(request,"register.html")

    return render(request,"register.html")

def login(request):
    if request.method=="POST":
        uname=request.POST['uname']
        ps=request.POST['psw']
        user=auth.authenticate(username=uname,password=ps)
        if user is not None:
            auth.login(request,user)
            return HttpResponseRedirect('data')
        else:
            messages.info(request,"Invalid Credentials")
            return render(request,"login.html")
    return render(request,"login.html")


def logout(request):
    auth.logout(request)
    return  HttpResponseRedirect("/")


def data(request):
    if request.method=="POST":
        category=request.POST['cat']
        amount=float(request.POST['amt'])
        latitude=float(request.POST['lat'])
        longitude=float(request.POST['long'])
        mlatitude=float(request.POST['mlat'])
        mlongitude=float(request.POST['mlong'])
        job=request.POST['job']
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        df=pd.read_csv("static/dataset/CreditCard.csv")
        print(df.head())
        df['is_fraud_cat'] = df['is_fraud'].apply(lambda x: "Fraud" if x==1 else "No Fraud")

        is_fraud_values = df['is_fraud_cat'].value_counts()

        plt.figure(figsize=(7,7))
        plt.pie(is_fraud_values, labels=is_fraud_values.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("deep", n_colors=len(is_fraud_values)))
        plt.title('% of Fraudulent vs Non-fraudulent transactions')
        plt.show()
        df[df['is_fraud_cat']=="Fraud"]["job"].value_counts(sort=True,ascending=False).head(10).plot(kind="bar",x='job', y=df['is_fraud_cat']=="Fraud", color=['red', 'green', 'blue', 'orange', 'purple'])
        plt.title("Top of Credit Card Frauds by Job")
        plt.show()
        from sklearn.preprocessing import LabelEncoder
        l=LabelEncoder()
        cat=l.fit_transform(df["category"])
        job1=l.fit_transform(df["job"])

        category_1=l.fit_transform([category])
        job_1=l.fit_transform([job])

        df=df.drop(["is_fraud_cat","job","category"],axis=1)
        df["Category"]=cat
        df["Jobs"]=job1

        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score

        X=df.drop("is_fraud",axis=1)
        y=df["is_fraud"]
        print(X[0:2])
        print(y[0:2])
        X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.35)
        from sklearn.linear_model import LogisticRegression
        log=LogisticRegression()
        log.fit(X_train,y_train)
        pred_log=log.predict(X_test)
        from sklearn.neighbors import KNeighborsClassifier
        knn=KNeighborsClassifier()
        knn.fit(X_train,y_train)
        pred_knn=knn.predict(X_test)
        from sklearn.naive_bayes import GaussianNB
        gn=GaussianNB()
        gn.fit(X_train,y_train)
        pred_gn=gn.predict(X_test)
        from sklearn.ensemble import RandomForestClassifier
        rf=RandomForestClassifier()
        rf.fit(X_train,y_train)
        pred_rf=rf.predict(X_test)
        print(X_test[0:10])
        print(pred_rf[0:10])

        print("Accuracy Score")
        print("Logistic Regression: ",accuracy_score(pred_log,y_test))
        print("KNN : ",accuracy_score(pred_knn,y_test))
        print("Random Forest: ",accuracy_score(pred_rf,y_test))
        print("Naive Bayes: ",accuracy_score(pred_gn,y_test))
        import numpy as np
        from sklearn.metrics import confusion_matrix
        def plot_confusion_matrix(cm, title='CONFUSION MATRIX', cmap=plt.cm.Reds):
            target_names=['Fraud','No Fraud']
            plt.imshow(cm, interpolation='nearest', cmap=cmap)
            plt.title(title)
            plt.colorbar()
            tick_marks = np.arange(len(target_names))
            plt.xticks(tick_marks, target_names, rotation=45)
            plt.yticks(tick_marks, target_names)
            plt.tight_layout()
            plt.ylabel('True label')
            plt.xlabel('Predicted label')
        confusionMatrix = confusion_matrix(y_test, pred_log)
        print('Confusion matrix, Logisitc Regression')
        print(confusionMatrix)
        plot_confusion_matrix(confusionMatrix)
        plt.show()
        X=df.drop(["Category","Jobs","is_fraud"],axis=1)
        y=df["is_fraud"]
        from sklearn.linear_model import LogisticRegression
        rf=LogisticRegression()
        rf.fit(X,y)
        import numpy as np
        pred_data=np.array([[amount,latitude,longitude,mlatitude,mlongitude]],dtype=object)
        prediction=rf.predict(pred_data)
        print(prediction)
        if prediction==[1]:
            prediction_data="Fraud"
            print(prediction_data)
        else:
            prediction_data="No Fraud"
            print(prediction_data)
        cc=Credit_Card.objects.create(category=category,amount=amount,
        latitude=latitude,longitude=longitude,merchant_latitude=mlatitude,
        merchant_longitude=mlongitude,jobs=job,prediction=prediction_data)
        cc.save()
       
        return render(request,"predict.html",{"category":category,"job":job,"latitude":latitude,"longitude":longitude,"mlatitude":mlatitude,
        "mlongitude":mlongitude,"prediction":prediction,"amount":amount,"prediction_data":prediction_data})
    return render(request,"data.html")

def predict(request):
    return render(request,"predict.html")

def contact(request):
    return render(request,"contact.html")

def adminhome(request):
    cc=Credit_Card.objects.all()
    return render(request,"adminhome.html",{"cc":cc})