export const SignIn = () => `
  <section class="card max-w-md mx-auto">
    <h2 class="text-xl font-bold">Sign In</h2>
    <form id="signInForm" class="mt-4 space-y-3">
      <div>
        <label class="label" for="email">Email</label>
        <input id="email" name="email" type="email" required class="input" placeholder="you@example.com" />
      </div>
      <div>
        <label class="label" for="password">Password</label>
        <input id="password" name="password" type="password" required class="input" />
      </div>
      <button class="btn-primary w-full" type="submit">Sign In</button>
    </form>
    <p class="mt-3 text-sm text-slate-400">Don't have an account? <a class="underline" href="#/register">Register here</a></p>
  </section>
`;