export const SetupFilesystem = () => `
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
`;