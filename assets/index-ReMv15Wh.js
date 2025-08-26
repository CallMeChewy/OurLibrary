var b=t=>{throw TypeError(t)};var v=(t,e,a)=>e.has(t)||b("Cannot "+a);var y=(t,e,a)=>e.has(t)?b("Cannot add the same private member more than once"):e instanceof WeakSet?e.add(t):e.set(t,a);var d=(t,e,a)=>(v(t,e,"access private method"),a);(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const s of document.querySelectorAll('link[rel="modulepreload"]'))r(s);new MutationObserver(s=>{for(const i of s)if(i.type==="childList")for(const o of i.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&r(o)}).observe(document,{childList:!0,subtree:!0});function a(s){const i={};return s.integrity&&(i.integrity=s.integrity),s.referrerPolicy&&(i.referrerPolicy=s.referrerPolicy),s.crossOrigin==="use-credentials"?i.credentials="include":s.crossOrigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function r(s){if(s.ep)return;s.ep=!0;const i=a(s);fetch(s.href,i)}})();const f=t=>document.querySelector(t),x=t=>{const e=document.getElementById("view");e&&(e.innerHTML=t)},p=(t,e)=>{const a=f(t);a&&a.addEventListener("submit",async r=>{r.preventDefault();const s=new FormData(a),i=Object.fromEntries(s);a.querySelectorAll('input[type="checkbox"]').forEach(o=>{o.checked&&(i[o.name]=o.value||"on")});try{await e(i)}catch(o){console.error("Form handler error:",o)}})};var c,u;class g{constructor(){y(this,c);this.user=null,this.listeners=new Set}onAuthStateChanged(e){return this.listeners.add(e),e(this.user),()=>this.listeners.delete(e)}async signUp({email:e,password:a}){return this.user={uid:"mock-uid",email:e,emailVerified:!1},d(this,c,u).call(this),this.user}async signIn({email:e}){return this.user={uid:"mock-uid",email:e,emailVerified:!0},d(this,c,u).call(this),this.user}async sendEmailVerification(){setTimeout(()=>{this.user&&(this.user.emailVerified=!0,d(this,c,u).call(this))},1e3)}async reload(){return this.user}async signOut(){this.user=null,d(this,c,u).call(this)}}c=new WeakSet,u=function(){this.listeners.forEach(e=>e(this.user))};const n=new g,w=t=>{const e=!!t,a=!!(t&&t.emailVerified),r=e&&a&&!localStorage.getItem("ol:setupComplete");return{isSignedIn:e,isEmailVerified:a,needsSetup:r}},S=()=>`
  <section class="card max-w-2xl mx-auto text-center">
    <h2 class="text-3xl font-bold mb-4">Welcome to OurLibrary</h2>
    <p class="text-lg mb-6">Your personal educational library platform</p>
    <div class="space-x-4">
      <a href="#/register" class="btn-primary">Get Started</a>
      <a href="#/signin" class="btn-secondary">Sign In</a>
    </div>
  </section>
`,E=()=>`
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
`,L=()=>`
  <section class="card max-w-md mx-auto text-center">
    <h2 class="text-xl font-bold">Check Your Email</h2>
    <p class="mt-4 text-slate-300">We've sent a verification email to your inbox.</p>
    <p class="mt-2 text-sm text-slate-400">Please check your email and follow the instructions to verify your account.</p>
    <div class="mt-6">
      <a href="#/verify" class="btn-primary">Go to verification page</a>
    </div>
  </section>
`,I=t=>`
  <section class="card max-w-md mx-auto text-center">
    <h2 class="text-xl font-bold">Email Verification</h2>
    
    ${t?`
      <p class="mt-4 text-slate-300">✅ Your email has been verified!</p>
      <p class="mt-2 text-sm text-slate-400">Redirecting to setup...</p>
    `:`
      <p class="mt-4 text-slate-300">Please verify your email address to continue.</p>
      <div class="mt-6 space-y-3">
        <button id="refresh" class="btn-primary w-full">Check verification status</button>
        <button id="resend" class="btn-secondary w-full">Resend verification email</button>
      </div>
    `}
  </section>
`,C=()=>`
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
`,F=()=>`
  <section class="card max-w-2xl mx-auto">
    <h2 class="text-xl font-bold">Set Up Your Personal Library</h2>
    <div class="mt-4 space-y-4">
      <p class="text-slate-300">Choose a folder on your computer to store your library files:</p>
      
      <div class="bg-slate-800 rounded-xl p-4">
        <h3 class="font-semibold mb-2">What we'll create:</h3>
        <ul class="text-sm text-slate-300 space-y-1">
          <li>📚 Books/ - Your PDF and document files</li>
          <li>🖼️ Covers/ - Book cover thumbnails</li>
          <li>💾 Database/ - Library catalog and metadata</li>
          <li>📥 Downloads/ - Temporary download area</li>
        </ul>
      </div>
      
      <form id="fsForm" class="mt-6">
        <div>
          <label class="label" for="folder">Library Folder Path</label>
          <input id="folder" name="folder" type="text" required class="input" placeholder="e.g., /Users/yourname/OurLibrary" />
        </div>
        
        <button type="submit" class="btn-primary w-full mt-4">Create Library Structure</button>
      </form>
      
      <p class="text-xs text-slate-400 mt-2">
        💡 Tip: Choose a location with plenty of storage space for your educational content.
      </p>
    </div>
  </section>
`,O=()=>`
  <div class="space-y-6">
    <header class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">Your Library</h2>
        <p class="text-slate-400">Manage your educational content collection</p>
      </div>
      <button id="signOut" class="btn-secondary">Sign Out</button>
    </header>
    
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Library Statistics</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-slate-800 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-indigo-400">0</div>
          <div class="text-sm text-slate-400">Books</div>
        </div>
        <div class="bg-slate-800 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-green-400">0</div>
          <div class="text-sm text-slate-400">Categories</div>
        </div>
        <div class="bg-slate-800 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-blue-400">0</div>
          <div class="text-sm text-slate-400">Recently Added</div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Quick Actions</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button class="btn-primary">Add New Books</button>
        <button class="btn-secondary">Scan Directory</button>
        <button class="btn-secondary">Import from URL</button>
        <button class="btn-secondary">Manage Categories</button>
      </div>
    </div>
    
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Recent Books</h3>
      <div class="text-center py-8 text-slate-400">
        📚 Your books will appear here once you add them to your library
      </div>
    </div>
  </div>
`,k=()=>`
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
`,h={"/":()=>S(),"/register":()=>E(),"/registered":()=>L(),"/verify":t=>I(t==null?void 0:t.isEmailVerified),"/setup/consent":()=>C(),"/setup/filesystem":()=>F(),"/app":()=>O(),"/signin":()=>k()};function l(t){location.hash!==`#${t}`&&(location.hash=`#${t}`),m()}function P(t){p("#regForm",async s=>{const i=await n.signUp({email:s.email,password:s.password});await n.sendEmailVerification(i),l("/registered")}),p("#signInForm",async s=>{await n.signIn({email:s.email,password:s.password}),m()});const e=f("#resend");e&&e.addEventListener("click",()=>n.sendEmailVerification());const a=f("#refresh");a&&a.addEventListener("click",async()=>{await n.reload(),m()}),p("#consentForm",s=>{"agree"in s&&(localStorage.setItem("ol:consent","1"),l("/setup/filesystem"))}),p("#fsForm",s=>{s.folder&&(localStorage.setItem("ol:libraryFolder",s.folder),localStorage.setItem("ol:setupComplete","1"),l("/app"))});const r=f("#signOut");r&&r.addEventListener("click",async()=>{await n.signOut(),localStorage.removeItem("ol:setupComplete"),l("/")})}async function m(){const t=await new Promise(s=>{let i=null;i=n.onAuthStateChanged(o=>{i&&i(),s(o)})}),e=w(t),a=(location.hash||"#/").slice(1);if(!e.isSignedIn&&["/setup/consent","/setup/filesystem","/app","/verify"].includes(a)){l("/register");return}if(e.isSignedIn&&!e.isEmailVerified&&a!=="/verify"){l("/verify");return}if(e.needsSetup&&!a.startsWith("/setup")){l("/setup/consent");return}const r=h[a]?h[a](e):'<p class="card">Not found</p>';x(r),P()}window.addEventListener("hashchange",m);document.addEventListener("DOMContentLoaded",()=>{const t=document.getElementById("year");t&&(t.textContent=new Date().getFullYear()),m()});
