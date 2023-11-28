// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.6.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.6.0/firebase-analytics.js";
import { getAuth, signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider }
    from "https://www.gstatic.com/firebasejs/10.6.0/firebase-auth.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyDo3NLdB2O5y_LL-_tLld4qc7AKR3Amlxs",
    authDomain: "test1-de0f3.firebaseapp.com",
    databaseURL: "https://test1-de0f3-default-rtdb.firebaseio.com",
    projectId: "test1-de0f3",
    storageBucket: "test1-de0f3.appspot.com",
    messagingSenderId: "54687048158",
    appId: "1:54687048158:web:27e99ee6cfca514244bd4f",
    measurementId: "G-4T5242MBQG"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

const provider = new GoogleAuthProvider();
const auth = getAuth();

function sendPost(url, params) {
    var form = document.createElement('form');
    form.setAttribute('method', 'post');
    form.setAttribute('action', url);

    for(var key in params) {
        var hiddenField = document.createElement('input');
        hiddenField.setAttribute('type', 'hidden');
        hiddenField.setAttribute('name', key);
        hiddenField.setAttribute('value', params[key]);
        form.appendChild(hiddenField);
    }
    document.body.appendChild(form);
    form.submit();
}

//이메일 로그인
document.getElementById("signInButton").addEventListener('click', (event) => {
    event.preventDefault() //새로고침 방지
    const signInEmail = document.getElementById("signInEmail").value
    const signInPassword = document.getElementById("signInPassword").value

    signInWithEmailAndPassword(auth, signInEmail, signInPassword)
        .then((userCredential) => {
            // Signed in 
            const user = userCredential.user;

            console.log("성공");
            // ...
            // 로그인 성공하면 "/home"로 이메일을 POST로 보냄
            sendPost('/home', { email: signInEmail });
        })
        .catch((error) => {
            alert('로그인 실패');
            const errorCode = error.code;
            const errorMessage = error.message;
        });
})

//구글 로그인
document.getElementById("googleLogin").addEventListener("click", () => {
    signInWithPopup(auth, provider)
        .then((result) => {
            // This gives you a Google Access Token. You can use it to access the Google API.
            const credential = GoogleAuthProvider.credentialFromResult(result);
            const token = credential.accessToken;
            // The signed-in user info.
            const user = result.user;
            // IdP data available using getAdditionalUserInfo(result)
            // ...
            //console.log(user.email);
            // 로그인 성공하면 "/home"로 이메일을 POST로 보냄
            let emailAsString = String(user.email);
            sendPost('/home', { email: emailAsString });
        }).catch((error) => {
            // Handle Errors here.
            const errorCode = error.code;
            const errorMessage = error.message;
            // The email of the user's account used.
            const email = error.customData.email;
            // The AuthCredential type that was used.
            const credential = GoogleAuthProvider.credentialFromError(error);
            // ...
            console.log(error);
        });
});