/**
 * Pluggable auth facade. Two adapters:
 *  - MockAdapter: default for local dev & e2e tests
 *  - FirebaseAdapter: production (requires env config)
 */
import { MockAdapter } from './MockAdapter.js';
import { FirebaseAdapter } from './FirebaseAdapter.js';

const MODE = import.meta.env.VITE_AUTH_MODE || 'mock'; // 'mock' | 'firebase'

export const auth = MODE === 'firebase' ? new FirebaseAdapter() : new MockAdapter();

export const deriveState = (u) => {
  const isSignedIn = !!u;
  const isEmailVerified = !!(u && u.emailVerified);
  const needsSetup = isSignedIn && isEmailVerified && !localStorage.getItem('ol:setupComplete');
  return { isSignedIn, isEmailVerified, needsSetup };
};