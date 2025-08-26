export class MockAdapter {
  constructor() {
    this.user = null;
    this.listeners = new Set();
  }
  
  onAuthStateChanged(cb) {
    this.listeners.add(cb);
    cb(this.user);
    return () => this.listeners.delete(cb);
  }
  
  async signUp({ email, password }) {
    // naive mock
    this.user = { uid: 'mock-uid', email, emailVerified: false };
    this.#emit();
    return this.user;
  }
  
  async signIn({ email }) {
    this.user = { uid: 'mock-uid', email, emailVerified: true };
    this.#emit();
    return this.user;
  }
  
  async sendEmailVerification() {
    // in mock, immediately becomes verified after 1s
    setTimeout(() => {
      if (this.user) {
        this.user.emailVerified = true;
        this.#emit();
      }
    }, 1000);
  }
  
  async reload() {
    // no-op for mock
    return this.user;
  }
  
  async signOut() {
    this.user = null;
    this.#emit();
  }
  
  #emit() { this.listeners.forEach(cb => cb(this.user)); }
}