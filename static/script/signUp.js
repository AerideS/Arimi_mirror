// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.6.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.6.0/firebase-analytics.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.6.0/firebase-auth.js";
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

const auth = getAuth();

//회원가입
document.getElementById("signUpButton").addEventListener('click', (event) => {
    event.preventDefault() //form은 서버의 정보를 제공하는 것이라서 새로고침 현상 발생하는데 이런 현상막음
    const signUpEmail = document.getElementById("signUpEmail").value
    const signUpPassword = document.getElementById("signUpPassword").value

    createUserWithEmailAndPassword(auth, signUpEmail, signUpPassword)
        .then((userCredential) => {
            // Signed in 
            const user = userCredential.user;
            // ...
            window.location.href = "/";
        })
        .catch((error) => {
            console.log('회원가입 실패')
            const errorCode = error.code;
            const errorMessage = error.message;
            // ..
        });

})