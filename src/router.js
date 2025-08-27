import { mount, withForm, $ } from './ui/dom.js';
import { auth, deriveState } from './auth/AuthService.js';
import { NewMainPage } from './pages/NewMainPage.js';
import { RegistrationModal } from './pages/RegistrationModal.js';
import { RegistrationComplete } from './pages/RegistrationComplete.js';
import { EmailVerification } from './pages/EmailVerification.js';
import { SetupConsent } from './pages/SetupConsent.js';
import { SetupFilesystem } from './pages/SetupFilesystem.js';
import { DesktopLibrary } from './pages/DesktopLibrary.js';
import { SignIn } from './pages/SignIn.js';

const routes = {
  '/': () => NewMainPage(),
  '/register': () => RegistrationModal(),
  '/registered': () => RegistrationComplete(),
  '/verify': (state) => EmailVerification(state?.isEmailVerified),
  '/setup/consent': () => SetupConsent(),
  '/setup/filesystem': () => SetupFilesystem(),
  '/app': () => DesktopLibrary(),
  '/signin': () => SignIn(),
};

function navigate(path) {
  if (location.hash !== `#${path}`) location.hash = `#${path}`;
  render();
}

function installHandlers(state) {
  // Registration
  withForm('#regForm', async (data) => {
    const user = await auth.signUp({ email: data.email, password: data.password });
    await auth.sendEmailVerification(user);
    navigate('/registered');
  });

  // Sign-in
  withForm('#signInForm', async (data) => {
    await auth.signIn({ email: data.email, password: data.password });
    render();
  });

  // Verification page
  const resend = $('#resend');
  if (resend) resend.addEventListener('click', () => auth.sendEmailVerification());

  const refresh = $('#refresh');
  if (refresh) refresh.addEventListener('click', async () => {
    await auth.reload();
    render();
  });

  // Setup consent
  withForm('#consentForm', (data) => {
    if (!('agree' in data)) return;
    localStorage.setItem('ol:consent', '1');
    navigate('/setup/filesystem');
  });

  // Setup filesystem
  withForm('#fsForm', (data) => {
    if (!data.folder) return;
    localStorage.setItem('ol:libraryFolder', data.folder);
    localStorage.setItem('ol:setupComplete', '1');
    navigate('/app');
  });

  // Sign out
  const signOut = $('#signOut');
  if (signOut) signOut.addEventListener('click', async () => {
    await auth.signOut();
    localStorage.removeItem('ol:setupComplete');
    navigate('/');
  });
}

export async function render() {
  const user = await new Promise((resolve) => {
    let off = null;
    off = auth.onAuthStateChanged((u) => {
      if (off) off();
      resolve(u);
    });
  });
  const state = deriveState(user);
  const path = (location.hash || '#/').slice(1);

  // Guards - enforce 7-step flow
  if (!state.isSignedIn && ['/setup/consent','/setup/filesystem','/app','/verify'].includes(path)) {
    navigate('/register');
    return;
  }
  if (state.isSignedIn && !state.isEmailVerified && path !== '/verify') {
    navigate('/verify');
    return;
  }
  if (state.needsSetup && !path.startsWith('/setup')) {
    navigate('/setup/consent');
    return;
  }

  const view = routes[path] ? routes[path](state) : '<p class="card">Not found</p>';
  mount(view);
  installHandlers(state);
}

window.addEventListener('hashchange', render);