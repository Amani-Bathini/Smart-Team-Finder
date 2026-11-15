/**
 * Smart Team Finder - Client-Side Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNavigation();
  initPasswordToggles();
  initPasswordStrengthMeter();
  initSkillTagPreviews();
  formatSkillsOnCards();
  initJoinRequestInterceptors();
  initActionConfirmations();
  initAlertDismissals();
  initDynamicAvatars();
  initUserProfileDropdown();
});

/**
 * 0. Universal User Profile Dropdown
 */
function initUserProfileDropdown() {
  const profileBtn = document.getElementById('userProfileBtn');
  const profileDropdown = document.getElementById('userProfileDropdown');
  if (profileBtn && profileDropdown) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = profileDropdown.classList.contains('show');
      profileDropdown.classList.toggle('show');
      profileBtn.setAttribute('aria-expanded', !isOpen);
    });

    document.addEventListener('click', (e) => {
      if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
        profileDropdown.classList.remove('show');
        profileBtn.setAttribute('aria-expanded', 'false');
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && profileDropdown.classList.contains('show')) {
        profileDropdown.classList.remove('show');
        profileBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

/**
 * 1. Mobile Navigation Hamburger Menu
 */
function initMobileNavigation() {
  const header = document.querySelector('header, .app-header');
  if (!header) return;

  let nav = header.querySelector('nav, .nav-links');
  if (!nav) return;

  let toggleBtn = header.querySelector('.mobile-nav-toggle');
  if (!toggleBtn) {
    toggleBtn = document.createElement('button');
    toggleBtn.className = 'mobile-nav-toggle';
    toggleBtn.type = 'button';
    toggleBtn.setAttribute('aria-label', 'Toggle navigation menu');
    toggleBtn.innerHTML = `
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    `;
    header.appendChild(toggleBtn);
  }

  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    nav.classList.toggle('nav-open');
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (nav.classList.contains('nav-open') && !nav.contains(e.target) && !toggleBtn.contains(e.target)) {
      nav.classList.remove('nav-open');
    }
  });

  // Close on window resize
  window.addEventListener('resize', () => {
    if (window.innerWidth > 768 && nav.classList.contains('nav-open')) {
      nav.classList.remove('nav-open');
    }
  });
}

/**
 * 2. Password Visibility Toggle
 */
function initPasswordToggles() {
  const passwordInputs = document.querySelectorAll('input[type="password"]');

  passwordInputs.forEach((input) => {
    // Check if already wrapped
    let wrapper = input.parentElement;
    if (!wrapper.classList.contains('password-input-wrapper')) {
      wrapper = document.createElement('div');
      wrapper.className = 'password-input-wrapper';
      input.parentNode.insertBefore(wrapper, input);
      wrapper.appendChild(input);
    }

    if (!wrapper.querySelector('.password-toggle-btn')) {
      const toggleBtn = document.createElement('button');
      toggleBtn.type = 'button';
      toggleBtn.className = 'password-toggle-btn';
      toggleBtn.setAttribute('aria-label', 'Show/Hide password');
      toggleBtn.innerHTML = eyeIcon(false);

      toggleBtn.addEventListener('click', () => {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        toggleBtn.innerHTML = eyeIcon(isPassword);
      });

      wrapper.appendChild(toggleBtn);
    }
  });
}

function eyeIcon(show) {
  if (show) {
    // Eye off (hide)
    return `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
        <line x1="1" y1="1" x2="23" y2="23"></line>
      </svg>
    `;
  }
  // Eye on (show)
  return `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
      <circle cx="12" cy="12" r="3"></circle>
    </svg>
  `;
}

/**
 * 3. Password Strength Meter (for Registration)
 */
function initPasswordStrengthMeter() {
  const registerForm = document.querySelector('form[action*="register"]');
  if (!registerForm) return;

  const passwordInput = registerForm.querySelector('input[name="password"]');
  if (!passwordInput) return;

  const meterContainer = document.createElement('div');
  meterContainer.className = 'password-strength-container';
  meterContainer.innerHTML = `
    <div class="password-strength-bar">
      <div class="password-strength-fill" id="pwdStrengthFill"></div>
    </div>
    <span class="password-strength-text" id="pwdStrengthText">Enter a strong password</span>
  `;

  const wrapper = passwordInput.closest('.password-input-wrapper') || passwordInput;
  wrapper.parentNode.insertBefore(meterContainer, wrapper.nextSibling);

  const fill = meterContainer.querySelector('#pwdStrengthFill');
  const text = meterContainer.querySelector('#pwdStrengthText');

  passwordInput.addEventListener('input', () => {
    const val = passwordInput.value;
    if (!val) {
      fill.style.width = '0%';
      fill.style.backgroundColor = 'transparent';
      text.textContent = 'Enter a strong password';
      return;
    }

    let score = 0;
    if (val.length >= 6) score++;
    if (val.length >= 10) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    if (score <= 2) {
      fill.style.width = '33%';
      fill.style.backgroundColor = '#ef4444'; // Red
      text.textContent = 'Weak password (add numbers, caps & symbols)';
      text.style.color = '#ef4444';
    } else if (score <= 4) {
      fill.style.width = '66%';
      fill.style.backgroundColor = '#f59e0b'; // Amber
      text.textContent = 'Moderate password';
      text.style.color = '#d97706';
    } else {
      fill.style.width = '100%';
      fill.style.backgroundColor = '#10b981'; // Green
      text.textContent = 'Strong password!';
      text.style.color = '#059669';
    }
  });
}

/**
 * 4. Interactive Live Skill Tag Previews
 */
function initSkillTagPreviews() {
  const skillInputs = document.querySelectorAll('input[name="skills"], textarea[name="required_skills"]');

  skillInputs.forEach((input) => {
    const previewContainer = document.createElement('div');
    previewContainer.className = 'skill-tags-preview';
    input.parentNode.insertBefore(previewContainer, input.nextSibling);

    const updatePreview = () => {
      const raw = input.value || '';
      const tags = raw
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      previewContainer.innerHTML = '';
      tags.forEach((tag) => {
        const span = document.createElement('span');
        span.className = 'tag-badge';
        span.textContent = tag;
        previewContainer.appendChild(span);
      });
    };

    input.addEventListener('input', updatePreview);
    updatePreview();
  });
}

/**
 * 5. Format Comma-Separated Skills into Badges on Existing Cards
 */
function formatSkillsOnCards() {
  const paragraphs = document.querySelectorAll('p, div');

  paragraphs.forEach((el) => {
    // Only target direct paragraphs displaying skills
    if (el.children.length === 1 && (el.children[0].tagName === 'B' || el.children[0].tagName === 'STRONG')) {
      const headerText = el.children[0].textContent.toLowerCase();
      if (headerText.includes('skill')) {
        const fullText = el.textContent;
        const colonIdx = fullText.indexOf(':');
        if (colonIdx !== -1) {
          const skillsList = fullText.substring(colonIdx + 1).trim();
          if (skillsList && skillsList !== 'None' && skillsList !== 'Not Added' && skillsList !== 'Not provided') {
            const skills = skillsList.split(',').map((s) => s.trim()).filter((s) => s.length > 0);
            if (skills.length > 0) {
              const labelText = el.children[0].textContent;
              const wrapper = document.createElement('div');
              wrapper.style.margin = '0.4rem 0 0.8rem 0';
              wrapper.innerHTML = `<strong>${labelText}</strong> `;
              
              const tagsDiv = document.createElement('div');
              tagsDiv.className = 'skills-wrapper';
              tagsDiv.style.display = 'inline-flex';
              tagsDiv.style.flexWrap = 'wrap';
              tagsDiv.style.gap = '0.35rem';
              tagsDiv.style.marginTop = '0.3rem';

              skills.forEach((skill) => {
                const pill = document.createElement('span');
                pill.className = 'skill-pill';
                pill.textContent = skill;
                tagsDiv.appendChild(pill);
              });

              wrapper.appendChild(tagsDiv);
              el.replaceWith(wrapper);
            }
          }
        }
      }
    }
  });
}

/**
 * 6. Smart Join Request Interceptor
 * Ensures links to /request_to_join/<id> post properly even if rendered as <a>
 */
function initJoinRequestInterceptors() {
  // Find any <a> tags pointing to request_to_join
  document.querySelectorAll('a[href*="request_to_join"], a.join-btn').forEach((link) => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href && href.includes('request_to_join')) {
        e.preventDefault();
        
        if (confirm('Are you sure you want to request to join this team?')) {
          // Create and submit a dynamic POST form
          const form = document.createElement('form');
          form.method = 'POST';
          form.action = href;
          document.body.appendChild(form);
          form.submit();
        }
      }
    });
  });

  // Also confirm standard join_team forms
  document.querySelectorAll('form[action*="join-team"], form[action*="join_team"]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      if (!confirm('Do you want to join this team?')) {
        e.preventDefault();
      }
    });
  });
}

/**
 * 7. Action Confirmations for Accept & Reject
 */
function initActionConfirmations() {
  document.querySelectorAll('form[action*="reject_request"]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      if (!confirm('Are you sure you want to reject this join request?')) {
        e.preventDefault();
      }
    });
  });

  document.querySelectorAll('form[action*="accept_request"]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      if (!confirm('Accept this developer as a team member?')) {
        e.preventDefault();
      }
    });
  });
}

/**
 * 8. Dismissable Alerts and Flash Messages
 */
function initAlertDismissals() {
  const alerts = document.querySelectorAll('.alert, .message, .flash-message');

  alerts.forEach((alert) => {
    if (!alert.querySelector('.alert-close')) {
      const closeBtn = document.createElement('button');
      closeBtn.type = 'button';
      closeBtn.className = 'alert-close';
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.innerHTML = '&times;';

      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      });

      alert.appendChild(closeBtn);
    }

    // Auto dismiss after 6 seconds
    setTimeout(() => {
      if (document.body.contains(alert)) {
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 400);
      }
    }, 6000);
  });
}

/**
 * 9. Dynamic Colorful Avatars for Developers
 */
function initDynamicAvatars() {
  const palette = [
    ['#4f46e5', '#7c3aed'],
    ['#0ea5e9', '#2563eb'],
    ['#10b981', '#059669'],
    ['#8b5cf6', '#d946ef'],
    ['#f59e0b', '#ea580c'],
    ['#ec4899', '#f43f5e']
  ];

  function getGradient(name) {
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const idx = Math.abs(hash) % palette.length;
    return `linear-gradient(135deg, ${palette[idx][0]} 0%, ${palette[idx][1]} 100%)`;
  }

  function getInitials(name) {
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  // Enhance developer cards in find_developers.html if not already styled
  document.querySelectorAll('div > h3').forEach((h3) => {
    const parent = h3.parentElement;
    if (parent && !parent.querySelector('.dev-avatar') && parent.parentElement && parent.parentElement.classList.contains('container')) {
      const name = h3.textContent.trim();
      const initials = getInitials(name);
      const gradient = getGradient(name);

      const headerDiv = document.createElement('div');
      headerDiv.style.display = 'flex';
      headerDiv.style.alignItems = 'center';
      headerDiv.style.gap = '1rem';
      headerDiv.style.marginBottom = '1rem';

      const avatar = document.createElement('div');
      avatar.className = 'dev-avatar';
      avatar.style.width = '48px';
      avatar.style.height = '48px';
      avatar.style.borderRadius = '50%';
      avatar.style.background = gradient;
      avatar.style.color = '#ffffff';
      avatar.style.display = 'flex';
      avatar.style.alignItems = 'center';
      avatar.style.justifyContent = 'center';
      avatar.style.fontWeight = '700';
      avatar.style.fontSize = '1.1rem';
      avatar.style.flexShrink = '0';
      avatar.style.boxShadow = '0 2px 6px rgba(0,0,0,0.15)';
      avatar.textContent = initials;

      parent.insertBefore(headerDiv, h3);
      headerDiv.appendChild(avatar);
      headerDiv.appendChild(h3);
      h3.style.margin = '0';
    }
  });
}

