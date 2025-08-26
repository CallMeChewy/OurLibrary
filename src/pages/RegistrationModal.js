export const RegistrationModal = () => `
  <section class="card max-w-md mx-auto">
    <h2 class="text-xl font-bold">Register</h2>
    <form id="regForm" class="mt-4 space-y-3">
      <div>
        <label class="label" for="email">Email</label>
        <input id="email" name="email" type="email" required class="input" placeholder="you@example.com" />
      </div>
      <div>
        <label class="label" for="password">Password</label>
        <input id="password" name="password" type="password" minlength="8" required class="input" />
      </div>
      <button class="btn-primary w-full" type="submit">Create account</button>
    </form>
    <p class="mt-3 text-sm text-slate-400">Already have an account? <a class="underline" href="#/signin">Sign in</a></p>
  </section>
`;