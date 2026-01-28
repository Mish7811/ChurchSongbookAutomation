import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Download, Upload, RefreshCw, Music, Eye, EyeOff } from 'lucide-react';

interface Song {
  sno: number;
  main: string;
  eng: string;
  slot: string;
}

interface WeekData {
  week_number: number;
  week_suffix: string;
  BN_offering: string;
  MN_offering: string;
  PN_offering: string;
  BN_SundayS: string;
  MN_SundayS: string;
  PN_SundayS: string;
}

function App() {
  const [selectedSlot, setSelectedSlot] = useState<'A' | 'B' | 'C'>('A');
  const [songs, setSongs] = useState<Song[]>([]);
  const [weekData, setWeekData] = useState<WeekData>({
    week_number: 1,
    week_suffix: 'st',
    BN_offering: '',
    MN_offering: '',
    PN_offering: '',
    BN_SundayS: '',
    MN_SundayS: '',
    PN_SundayS: ''
  });
  const [loading, setLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const bnTeachers = [
    'Kevin, Joshna & Priya',
    'Anusha, Ebinezar & Shalem',
    'Naphthali, Melvin & Priyanka',
    'Stella, Varshini & Nissi',
    'Devamma, Lenin, Priya & Anusha',
    'Other'
  ];

  const mnTeachers = [
    'John Lara & Jeyaprakash',
    'Mishal & John Peter',
    'Siromani & Keerthi',
    'Priya & Christy',
    'Other'
  ];

  const pnTeachers = [
    'Priya & Santhosh',
    'Kaviya & Jeni',
    'Reshma & Lilly',
    'Suganya & Kaviya',
    'Sudha & Kameshwari',
    'Other'
  ];

  // Fetch songs when slot changes
  useEffect(() => {
    fetchSongsForSlot(selectedSlot);
  }, [selectedSlot]);

  const fetchSongsForSlot = async (slot: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/songs?slot=${slot}`);
      const data = await response.json();
      
      if (data.success) {
        setSongs(data.songs);
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (err) {
      console.error('Failed to fetch songs:', err);
      alert('Failed to load songs');
    } finally {
      setLoading(false);
    }
  };

  const selectValueFor = (value: string, list: string[]) => {
    return list.includes(value) ? value : 'Other';
  };

  const handleWeekDataChange = (field: keyof WeekData, value: string | number) => {
    setWeekData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSongChange = (sno: number, field: 'main' | 'eng', value: string) => {
    setSongs(prev => prev.map(song =>
      song.sno === sno ? { ...song, [field]: value } : song
    ));
  };

  const getSuffixOptions = () => ['st', 'nd', 'rd', 'th'];

  const generateJSON = () => {
    return {
      slot: selectedSlot,
      week_number: weekData.week_number,
      week_suffix: weekData.week_suffix,
      BN_offering: weekData.BN_offering ? `${weekData.BN_offering} & Family` : '',
      MN_offering: weekData.MN_offering ? `${weekData.MN_offering} & Family` : '',
      PN_offering: weekData.PN_offering ? `${weekData.PN_offering} & Family` : '',
      BN_SundayS: weekData.BN_SundayS,
      MN_SundayS: weekData.MN_SundayS,
      PN_SundayS: weekData.PN_SundayS,
      songs: songs.map(s => ({
        sno: s.sno,
        main: s.main,
        eng: s.eng
      }))
    };
  };

  const downloadJSON = () => {
    const jsonData = generateJSON();
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `slot_${selectedSlot}_week_${weekData.week_number}_songs.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const updateGoogleSlides = async () => {
    if (songs.length === 0) {
      alert('No songs to update!');
      return;
    }

    setLoading(true);
    try {
      const payload = generateJSON();

      const response = await fetch(`${backendUrl}/update-slides`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        alert(`✅ ${result.message}\n${result.songsUpdated} songs marked as done.`);
        // Refresh to load next batch
        fetchSongsForSlot(selectedSlot);
      } else {
        alert(`⚠️ ${result.message}`);
      }
    } catch (err: any) {
      console.error('Error updating slides:', err);
      alert(`❌ Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Music className="w-8 h-8 text-purple-400" />
            <h1 className="text-4xl font-bold text-white">Church Songbook Generator</h1>
          </div>
          <p className="text-lg text-gray-300">Multi-slot pipeline system</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* LEFT COLUMN */}
          <div className="space-y-6">
            {/* Slot Selector */}
            <div className="bg-gray-800/60 backdrop-blur-sm border border-purple-700/30 rounded-xl shadow-2xl shadow-purple-900/20 p-6">
              <h2 className="text-2xl font-semibold text-white mb-4">Select Pipeline Slot</h2>
              <div className="flex gap-4">
                {['A', 'B', 'C'].map((slot) => (
                  <button
                    key={slot}
                    onClick={() => setSelectedSlot(slot as 'A' | 'B' | 'C')}
                    disabled={loading}
                    className={`flex-1 py-4 rounded-lg font-semibold text-lg transition-all ${
                      selectedSlot === slot
                        ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                        : 'bg-gray-700/50 text-gray-300 hover:bg-gray-700'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    Slot {slot}
                  </button>
                ))}
              </div>
              <p className="text-sm text-gray-400 mt-4 text-center">
                {songs.length} pending songs in Slot {selectedSlot}
              </p>
            </div>

            {/* Week Information */}
            <div className="bg-gray-800/60 backdrop-blur-sm border border-purple-700/30 rounded-xl shadow-2xl shadow-purple-900/20 p-6">
              <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
                📅 Week Information
              </h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Week Number
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={weekData.week_number}
                    onChange={(e) => handleWeekDataChange('week_number', parseInt(e.target.value) || 1)}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                    placeholder="1"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Week Suffix
                  </label>
                  <select
                    value={weekData.week_suffix}
                    onChange={(e) => handleWeekDataChange('week_suffix', e.target.value)}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                  >
                    {getSuffixOptions().map(suffix => (
                      <option key={suffix} value={suffix}>{suffix}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Offerings */}
            <div className="bg-gray-800/60 backdrop-blur-sm border border-purple-700/30 rounded-xl shadow-2xl shadow-purple-900/20 p-6">
              <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
                🎁 Offerings
              </h2>
              <p className="text-sm text-purple-300 mb-4 bg-purple-900/20 border border-purple-700/30 rounded-lg p-3">
                💡 Note: " & Family" will be automatically added to each offering name
              </p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    BN Offering (Name only)
                  </label>
                  <input
                    type="text"
                    value={weekData.BN_offering}
                    onChange={(e) => handleWeekDataChange('BN_offering', e.target.value)}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                    placeholder="John"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    MN Offering (Name only)
                  </label>
                  <input
                    type="text"
                    value={weekData.MN_offering}
                    onChange={(e) => handleWeekDataChange('MN_offering', e.target.value)}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                    placeholder="Doe"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    PN Offering (Name only)
                  </label>
                  <input
                    type="text"
                    value={weekData.PN_offering}
                    onChange={(e) => handleWeekDataChange('PN_offering', e.target.value)}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                    placeholder="Roger"
                  />
                </div>
              </div>
            </div>

            {/* Sunday Services */}
            <div className="bg-gray-800/60 backdrop-blur-sm border border-purple-700/30 rounded-xl shadow-2xl shadow-purple-900/20 p-6">
              <h2 className="text-2xl font-semibold text-white mb-6 flex items-center gap-2">
                ⛪ Sunday Services
              </h2>
              
              <div className="space-y-4">
                {/* BN SundayS */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    BN SundayS
                  </label>
                  <select
                    value={selectValueFor(weekData.BN_SundayS, bnTeachers)}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val === 'Other') {
                        handleWeekDataChange('BN_SundayS', '');
                      } else {
                        handleWeekDataChange('BN_SundayS', val);
                      }
                    }}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                  >
                    <option value="">— Select —</option>
                    {bnTeachers.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  
                  {(!bnTeachers.includes(weekData.BN_SundayS) || weekData.BN_SundayS === '') && (
                    <input
                      type="text"
                      placeholder="Enter custom BN Sunday teacher..."
                      value={weekData.BN_SundayS}
                      onChange={(e) => handleWeekDataChange('BN_SundayS', e.target.value)}
                      className="w-full mt-2 px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                    />
                  )}
                </div>
                
                {/* MN SundayS */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    MN SundayS
                  </label>
                  <select
                    value={selectValueFor(weekData.MN_SundayS, mnTeachers)}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val === 'Other') {
                        handleWeekDataChange('MN_SundayS', '');
                      } else {
                        handleWeekDataChange('MN_SundayS', val);
                      }
                    }}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                  >
                    <option value="">— Select —</option>
                    {mnTeachers.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  
                  {(!mnTeachers.includes(weekData.MN_SundayS) || weekData.MN_SundayS === '') && (
                    <input
                      type="text"
                      placeholder="Enter custom MN Sunday teacher..."
                      value={weekData.MN_SundayS}
                      onChange={(e) => handleWeekDataChange('MN_SundayS', e.target.value)}
                      className="w-full mt-2 px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                    />
                  )}
                </div>

                {/* PN SundayS */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    PN SundayS
                  </label>
                  <select
                    value={selectValueFor(weekData.PN_SundayS, pnTeachers)}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (val === 'Other') {
                        handleWeekDataChange('PN_SundayS', '');
                      } else {
                        handleWeekDataChange('PN_SundayS', val);
                      }
                    }}
                    className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                  >
                    <option value="">— Select —</option>
                    {pnTeachers.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  
                  {(!pnTeachers.includes(weekData.PN_SundayS) || weekData.PN_SundayS === '') && (
                    <input
                      type="text"
                      placeholder="Enter custom PN Sunday teacher..."
                      value={weekData.PN_SundayS}
                      onChange={(e) => handleWeekDataChange('PN_SundayS', e.target.value)}
                      className="w-full mt-2 px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200"
                    />
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN */}
          <div className="space-y-6">
            {/* Songs Display */}
            <div className="bg-gray-800/60 backdrop-blur-sm border border-purple-700/30 rounded-xl shadow-2xl shadow-purple-900/20 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-semibold text-white">
                  🎵 Songs - Slot {selectedSlot}
                </h2>
                <button
                  onClick={() => fetchSongsForSlot(selectedSlot)}
                  disabled={loading}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>

              {loading ? (
                <p className="text-gray-400 text-center py-8">Loading songs...</p>
              ) : songs.length === 0 ? (
                <p className="text-gray-400 text-center py-8">
                  No pending songs for this slot. All done! 🎉
                </p>
              ) : (
                <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                  {songs.map((song, index) => (
                    <div key={song.sno} className="bg-gray-700/40 border border-purple-600/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-medium text-gray-200">
                          Song {index + 1} <span className="text-sm text-gray-400">(S.No: {song.sno})</span>
                        </h3>
                      </div>
                      
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            Tamil/Telugu Lyrics
                          </label>
                          <textarea
                            value={song.main}
                            onChange={(e) => handleSongChange(song.sno, 'main', e.target.value)}
                            className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 resize-vertical"
                            rows={4}
                            placeholder="Enter main lyrics..."
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-300 mb-2">
                            English Lyrics
                          </label>
                          <textarea
                            value={song.eng}
                            onChange={(e) => handleSongChange(song.sno, 'eng', e.target.value)}
                            className="w-full px-4 py-3 bg-gray-700/60 border border-purple-600/50 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 resize-vertical"
                            rows={4}
                            placeholder="Enter English lyrics..."
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Preview and Actions */}
            <div className="bg-gray-800/60 backdrop-blur-sm border border-purple-700/30 rounded-xl shadow-2xl shadow-purple-900/20 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-white">JSON Preview</h2>
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors duration-200"
                >
                  {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  {showPreview ? 'Hide' : 'Show'}
                </button>
              </div>
              
              {showPreview && (
                <div className="bg-gray-900/80 border border-purple-600/30 rounded-lg p-4 max-h-96 overflow-y-auto mb-6">
                  <pre className="text-sm text-purple-300 whitespace-pre-wrap font-mono">
                    {JSON.stringify(generateJSON(), null, 2)}
                  </pre>
                </div>
              )}
              
              <div className="space-y-4">
                <button
                  onClick={downloadJSON}
                  className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-purple-600 to-blue-700 text-white px-6 py-4 rounded-lg hover:from-purple-700 hover:to-blue-800 transition-all duration-200 text-lg font-medium shadow-lg hover:shadow-purple-500/25"
                >
                  <Download className="w-5 h-5" />
                  Download JSON File
                </button>

                <button
                  onClick={updateGoogleSlides}
                  disabled={loading || songs.length === 0}
                  className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-green-600 to-emerald-700 text-white px-6 py-4 rounded-lg hover:from-green-700 hover:to-emerald-800 transition-all duration-200 text-lg font-medium shadow-lg hover:shadow-green-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Upload className="w-5 h-5" />
                  {loading ? 'Updating...' : `Update Slot ${selectedSlot} Slides`}
                </button>
              </div>
            </div>

            {/* Usage Instructions */}
            <div className="bg-gray-800/60 backdrop-blur-sm border border-purple-700/30 rounded-xl shadow-2xl shadow-purple-900/20 p-6">
              <h3 className="text-xl font-semibold text-white mb-4">📋 Instructions</h3>
              <div className="space-y-3 text-gray-300 text-sm">
                <p className="flex items-start gap-2">
                  <span className="text-purple-400 font-semibold">1.</span>
                  Select your pipeline slot (A, B, or C)
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-purple-400 font-semibold">2.</span>
                  Fill in week information and offerings
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-purple-400 font-semibold">3.</span>
                  Edit songs as needed (auto-loaded from Google Sheets)
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-purple-400 font-semibold">4.</span>
                  Click "Update Slides" to push to Google Slides
                </p>
                <p className="flex items-start gap-2">
                  <span className="text-purple-400 font-semibold">5.</span>
                  Completed songs are marked as "done" automatically
                </p>
                <div className="mt-4 p-3 bg-purple-900/20 border border-purple-700/30 rounded-lg">
                  <p className="text-purple-200 text-xs">
                    💡 Each slot uses its own reusable Google Slides deck. Three team members can work in parallel without conflicts.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;