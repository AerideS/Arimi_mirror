// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-analytics.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyAtVSKTGqw5jgGZAgFo1c5qCfMRJmSRAfE",
    authDomain: "example-login-9816b.firebaseapp.com",
    projectId: "example-login-9816b",
    storageBucket: "example-login-9816b.appspot.com",
    messagingSenderId: "285036230674",
    appId: "1:285036230674:web:0966c3665db7faa23b80cb",
    measurementId: "G-33RT9Q1ESQ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.4.0/firebase-auth.js";

const auth = getAuth();

document.getElementById("signUpButton").addEventListener('click', (event) => {
    event.preventDefault() //form은 서버의 정보를 제공하는 것이라서 새로고침 현상 발생하는데 이런 현상막음
    const signUpEmail = document.getElementById("signUpEmail").value
    const signUpPassword = document.getElementById("signUpPassword").value

    createUserWithEmailAndPassword(auth, signUpEmail, signUpPassword)
        .then((userCredential) => {
            console.log(userCredential)
            // Signed in 
            const user = userCredential.user;
            // ...
        })
        .catch((error) => {
            console.log('error')
            const errorCode = error.code;
            const errorMessage = error.message;
            // ..
        });
})

document.getElementById("signInButton").addEventListener('click', (event) => {
    event.preventDefault() //새로고침 방지
    const signInEmail = document.getElementById("signInEmail").value
    const signInPassword = document.getElementById("signInPassword").value

    signInWithEmailAndPassword(auth, signInEmail, signInPassword)
        .then((userCredential) => {
            console.log(userCredential)
            // Signed in 
            const user = userCredential.user;
            // ...
            //로그인 성공하면 홈페이지로 넘어감
            window.location.href = "home.html";
        })
        .catch((error) => {
            console.log('로그인 실패')
            const errorCode = error.code;
            const errorMessage = error.message;
        });
})

console.log(app)