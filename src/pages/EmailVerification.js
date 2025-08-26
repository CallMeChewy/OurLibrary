export const EmailVerification = (isVerified) => `
  <section class="card max-w-md mx-auto text-center">
    <h2 class="text-xl font-bold">Email Verification</h2>
    
    ${!isVerified ? `
      <p class="mt-4 text-slate-300">Please verify your email address to continue.</p>
      <div class="mt-6 space-y-3">
        <button id="refresh" class="btn-primary w-full">Check verification status</button>
        <button id="resend" class="btn-secondary w-full">Resend verification email</button>
      </div>
    ` : `
      <p class="mt-4 text-slate-300">✅ Your email has been verified!</p>
      <p class="mt-2 text-sm text-slate-400">Redirecting to setup...</p>
    `}
  </section>
`;