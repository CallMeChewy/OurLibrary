// New MainPage implementation matching LibraryFlow reference
export const NewMainPage = () => `
  <!-- Attribution Banner -->
  <div class="bg-black bg-opacity-50 text-center py-1 text-xs text-slate-400 mb-0">
    Sponsored by BowersWorld.com
  </div>

  <!-- Banner Image -->
  <div class="w-full h-64 overflow-hidden relative flex items-center mb-8">
    <img src="./ProjectHimalayaBanner.png" alt="Project Himalaya - Human and AI collaboration" class="w-full object-contain max-h-full" loading="lazy">
  </div>

  <!-- Main Content -->
  <div class="max-w-4xl mx-auto px-4 py-8">
    <!-- Project Name and Mission -->
    <div class="text-center mb-12">
      <h1 class="text-5xl font-bold text-white mb-6">OurLibrary</h1>
      <h2 class="text-2xl text-yellow-400 font-semibold mb-6">
        "Getting education into the hands of people who can least afford it"
      </h2>
      <p class="text-xl text-gray-300 leading-relaxed mb-6">
        OurLibrary is a free digital library platform providing access to thousands of educational 
        books and resources. Our mission is to break down barriers to education by offering 
        completely free access to quality educational content for students worldwide.
      </p>
      
      <!-- Call to Action Button -->
      <div class="mb-12">
        <a href="#/register" class="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-lg text-xl transition-all duration-300 transform hover:scale-105 shadow-lg inline-block">
          📚 Get Started - Join OurLibrary!
        </a>
        <p class="text-gray-400 mt-4 text-sm">
          Already a member? <a href="#/signin" class="text-blue-400 hover:text-blue-300 underline">Sign in here</a>
        </p>
      </div>
    </div>

    <!-- Library Features -->
    <h2 class="text-2xl font-bold text-white mb-8 text-center bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">What's In Our Library</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      <!-- Educational Materials -->
      <div class="bg-slate-800 bg-opacity-80 rounded-xl shadow-xl backdrop-blur-sm border border-slate-700 p-6 text-center transition-all duration-300 hover:shadow-2xl hover:transform hover:-translate-y-1">
        <div class="text-4xl mb-4">📚</div>
        <h3 class="text-xl font-semibold mb-3 text-white">Educational Books</h3>
        <p class="text-gray-300 text-sm">
          Thousands of textbooks, workbooks, and educational resources covering all subjects and grade levels.
        </p>
      </div>
      
      <!-- Multi-Language Support -->
      <div class="bg-slate-800 bg-opacity-80 rounded-xl shadow-xl backdrop-blur-sm border border-slate-700 p-6 text-center transition-all duration-300 hover:shadow-2xl hover:transform hover:-translate-y-1">
        <div class="text-4xl mb-4">🌍</div>
        <h3 class="text-xl font-semibold mb-3 text-white">Multiple Languages</h3>
        <p class="text-gray-300 text-sm">
          Books and materials available in multiple languages to serve diverse global communities.
        </p>
      </div>
      
      <!-- Offline Access -->
      <div class="bg-slate-800 bg-opacity-80 rounded-xl shadow-xl backdrop-blur-sm border border-slate-700 p-6 text-center transition-all duration-300 hover:shadow-2xl hover:transform hover:-translate-y-1">
        <div class="text-4xl mb-4">📱</div>
        <h3 class="text-xl font-semibold mb-3 text-white">Offline Access</h3>
        <p class="text-gray-300 text-sm">
          Download books for offline reading - perfect for areas with limited internet connectivity.
        </p>
      </div>
    </div>
  </div>
`;