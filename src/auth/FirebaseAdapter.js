// Firebase adapter placeholder - install firebase SDK when needed
export class FirebaseAdapter {
  constructor() {
    console.log('Firebase adapter would initialize here - install firebase SDK');
    // Will require: npm install firebase
  }
  
  onAuthStateChanged(cb) {
    console.log('Firebase onAuthStateChanged would be implemented here');
    return () => {};
  }
  
  async signUp({ email, password }) {
    throw new Error('Firebase adapter not implemented yet - install firebase SDK');
  }
  
  async signIn({ email, password }) {
    throw new Error('Firebase adapter not implemented yet - install firebase SDK');  
  }
  
  async sendEmailVerification() {
    throw new Error('Firebase adapter not implemented yet - install firebase SDK');
  }
  
  async reload() {
    throw new Error('Firebase adapter not implemented yet - install firebase SDK');
  }
  
  async signOut() {
    throw new Error('Firebase adapter not implemented yet - install firebase SDK');
  }
}