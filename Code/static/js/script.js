document.addEventListener('DOMContentLoaded', () => {
    // Rain animation creation
    const rainContainer = document.createElement('div');
    rainContainer.className = 'rain-animation';
    document.body.appendChild(rainContainer);
  
    function createRain() {
      for (let i = 0; i < 100; i++) {
        const drop = document.createElement('div');
        drop.className = 'rain-drop';
        drop.style.left = Math.random() * window.innerWidth + 'px';
        drop.style.animationDuration = Math.random() * 1 + 0.5 + 's';
        drop.style.animationDelay = Math.random() * -5 + 's';
        rainContainer.appendChild(drop);
      }
    }
  
    createRain();
  
    // Redirect to Sign-Up Page
    const toggleSignUp = document.getElementById('toggleSignUp');
    if (toggleSignUp) {
      toggleSignUp.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = 'signup.html'; // Redirect to the Sign-Up page
      });
    }

    // Login Form Submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
      loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        // Redirect to home page directly
        window.location.href = 'home.html';
      });
    }

    // Sign Up Form Submission
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
      signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        // Redirect to home page directly
        window.location.href = 'home.html';
      });
    }
});
