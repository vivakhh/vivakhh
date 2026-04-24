/* =============================================
   💊 YakMate Core Logic v2.0
   The Ethereal Laboratory System
   ============================================= */

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.17.2/firebase-app.js";
import { getAuth, onAuthStateChanged, GoogleAuthProvider, signInWithPopup, signOut } from "https://www.gstatic.com/firebasejs/9.17.2/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc, updateDoc, onSnapshot, collection, query, where } from "https://www.gstatic.com/firebasejs/9.17.2/firebase-firestore.js";

// Firebase Config (Restored from previous session)
const firebaseConfig = {
    apiKey: "AIzaSyDpnPJnErnrTloHk3HFrsXHORUMvAiOq5w",
    authDomain: "pill-sajangnim.firebaseapp.com",
    projectId: "pill-sajangnim",
    storageBucket: "pill-sajangnim.firebasestorage.app",
    messagingSenderId: "648268791992",
    appId: "1:648268791992:web:41a92580aa1a58ae6bb44d",
    measurementId: "G-VBYRGEEQ1C"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// State Management
let currentUser = null;
let medications = [
    { id: 'm1', name: '혈압약', time: '08:00', taken: false, type: 'morning' },
    { id: 'm2', name: '영양제', time: '13:00', taken: false, type: 'lunch' },
    { id: 'm3', name: '항생제', time: '19:00', taken: false, type: 'evening' }
];

// App Initialization
window.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initAppEvents();
    initServiceWorker();
    initKakao();
});

// Authentication Logic
function hideLoading() {
    const loading = document.getElementById('loading-screen');
    if (loading) loading.classList.remove('active');
}

async function initAuth() {
    // 세이프가드: 3.5초 후에도 응답 없으면 강제 전환
    const safeguard = setTimeout(() => {
        console.warn("Auth timeout - triggering safeguard...");
        hideLoading();
        if (!currentUser) navigateTo('landing');
    }, 3500);

    onAuthStateChanged(auth, async (user) => {
        clearTimeout(safeguard);
        hideLoading();
        
        if (user) {
            currentUser = user;
            console.log("Logged in as:", user.displayName);
            try {
                const greeting = document.getElementById('user-greeting');
                if (greeting) greeting.textContent = `안녕하세요, ${user.displayName || '사장님'} 👋`;
                await syncUserData();
            } catch (err) {
                console.error("Sync error:", err);
            }
            navigateTo('dashboard');
        } else {
            currentUser = null;
            navigateTo('landing');
        }
    });

    // Kakao 초기화 에러 방어
    try {
        if (typeof Kakao !== 'undefined' && !Kakao.isInitialized()) {
            Kakao.init('8088ae3fd80ed9cb91544a037bce4c63');
        }
    } catch (e) {
        console.error("Kakao Init Error:", e);
    }
}

function initKakao() {
    if (window.Kakao && !window.Kakao.isInitialized()) {
        window.Kakao.init('8183186259068065806'); // Restored API Key
    }
}

// Navigation Logic
window.navigateTo = (screenId) => {
    // 1. 모든 화면에서 active 제거 (강력하게)
    const allScreens = document.querySelectorAll('.screen');
    allScreens.forEach(s => {
        s.classList.remove('active');
    });
    
    // 2. 대상 화면 활성화
    const target = document.getElementById(`${screenId}-screen`);
    if (target) {
        target.classList.add('active');
        
        // 3. 네비게이션 바 제어
        const bottomNav = document.getElementById('bottom-nav');
        if (['dashboard', 'community', 'guardian'].includes(screenId)) {
            bottomNav?.classList.remove('hidden');
        } else {
            bottomNav?.classList.add('hidden');
        }
        
        if (screenId === 'dashboard') renderDashboard();
    }
};

// Rendering Dashboard
function renderDashboard() {
    const listContainer = document.getElementById('medication-list');
    listContainer.innerHTML = '';
    
    let takenCount = 0;
    
    medications.forEach(med => {
        const card = document.createElement('div');
        card.className = `med-card glass-card ${med.taken ? 'taken' : ''}`;
        card.innerHTML = `
            <div class="med-info">
                <p class="label-sm">${med.time}</p>
                <h5 class="title-sm">${med.name}</h5>
            </div>
        `;
        
        card.onclick = () => toggleMedication(med.id);
        listContainer.appendChild(card);
        
        if (med.taken) takenCount++;
    });
    
    updateBiometricRing(takenCount, medications.length);
}

// Signature Component Logic: Biometric Ring
function updateBiometricRing(current, total) {
    const percent = total > 0 ? (current / total) * 100 : 0;
    const circle = document.getElementById('progress-circle');
    const text = document.getElementById('medicon-count');
    const percentText = document.getElementById('daily-progress-percent');
    
    // SVG Dashoffset calculation (Circumference ~ 283)
    const offset = 283 - (283 * percent / 100);
    circle.style.strokeDashoffset = offset;
    
    text.textContent = `${current}/${total}`;
    percentText.textContent = `${Math.round(percent)}%`;
}

async function toggleMedication(id) {
    const med = medications.find(m => m.id === id);
    if (med) {
        med.taken = !med.taken;
        renderDashboard();
        // TODO: Sync with Firestore in production
    }
}

// Event Listeners
function initAppEvents() {
    document.getElementById('btn-start')?.addEventListener('click', () => {
        navigateTo('login');
    });

    document.getElementById('btn-google-login')?.addEventListener('click', () => {
        const provider = new GoogleAuthProvider();
        signInWithPopup(auth, provider);
    });

    document.getElementById('btn-kakao-login')?.addEventListener('click', () => {
        window.Kakao.Auth.login({
            success: (authObj) => {
                console.log("Kakao Auth Success:", authObj);
                // Handle Kakao Login in Firebase
            },
            fail: (err) => console.error(err)
        });
    });
}

// PWA & Service Worker
function initServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('./sw.js')
            .then(reg => console.log('SW Registered'))
            .catch(err => console.log('SW Failed', err));
    }
}

async function syncUserData() {
    if (!currentUser) return;
    const userRef = doc(db, "users", currentUser.uid);
    const snap = await getDoc(userRef);
    
    if (!snap.exists()) {
        await setDoc(userRef, {
            name: currentUser.displayName,
            email: currentUser.email,
            createdAt: new Date(),
            medications: medications
        });
    } else {
        const data = snap.data();
        if (data.medications) medications = data.medications;
    }
}
