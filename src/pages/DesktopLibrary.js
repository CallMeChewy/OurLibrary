export const DesktopLibrary = () => `
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
`;