export const SetupConsent = () => `
  <section class="card max-w-2xl mx-auto">
    <h2 class="text-xl font-bold">Terms of Service & Privacy</h2>
    <div class="mt-4 space-y-4">
      <p class="text-slate-300">Welcome to OurLibrary! Before we continue, please review our terms:</p>
      
      <div class="bg-slate-800 rounded-xl p-4 text-sm">
        <h3 class="font-semibold mb-2">Data Storage</h3>
        <p class="text-slate-300">Your library data is stored locally on your device. We don't upload your personal files to any server.</p>
        
        <h3 class="font-semibold mb-2 mt-4">Privacy</h3>
        <p class="text-slate-300">Your reading preferences and library organization remain private and under your control.</p>
        
        <h3 class="font-semibold mb-2 mt-4">Educational Use</h3>
        <p class="text-slate-300">This platform is designed for educational content management and personal learning.</p>
      </div>
      
      <form id="consentForm" class="mt-6">
        <label class="flex items-center space-x-3">
          <input type="checkbox" name="agree" class="rounded border-slate-600 bg-slate-800" required />
          <span class="text-sm">I agree to the terms of service and privacy policy</span>
        </label>
        
        <button type="submit" class="btn-primary w-full mt-4">Continue Setup</button>
      </form>
    </div>
  </section>
`;