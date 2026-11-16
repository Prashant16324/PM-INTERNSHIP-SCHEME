import React, { useState } from 'react';
import { studentsAPI } from '../../services/api';
import { useToast } from '../../context/ToastContext';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  Sparkles,
  Download,
  AlertCircle,
  ArrowRight,
  ListPlus,
} from 'lucide-react';

export const ResumeUploadPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [extractResult, setExtractResult] = useState<{
    filename: string;
    file_size_bytes: number;
    extracted_text_preview: string;
    detected_skills: string[];
    detected_education?: string;
    message: string;
  } | null>(null);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [isConfirming, setIsConfirming] = useState(false);

  const { showToast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Only PDF resume files (.pdf) are supported', 'warning');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        showToast('File size exceeds the 5MB limit', 'warning');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const result = await studentsAPI.uploadResume(selectedFile);
      setExtractResult(result);
      setSelectedSkills(result.detected_skills); // Pre-check all detected skills
      showToast('Resume processed successfully! Review detected skills below.', 'success');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to upload and parse resume.';
      showToast(msg, 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const toggleSkill = (skill: string) => {
    setSelectedSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const handleConfirmBatch = async () => {
    if (selectedSkills.length === 0) {
      showToast('Please select at least one skill to append to your profile', 'warning');
      return;
    }

    setIsConfirming(true);
    try {
      const added = await studentsAPI.confirmBatchSkills(selectedSkills);
      showToast(`Successfully added ${added.length} confirmed skills to your profile!`, 'success');
    } catch (err) {
      showToast('Failed to save skills to profile', 'error');
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Resume Upload & NLP Parsing</h1>
        <p className="text-xs text-slate-500">
          Upload your PDF resume. Our natural language processing pipeline extracts technical keywords and candidate competencies for review.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Upload Zone */}
        <div className="md:col-span-2 space-y-6">
          <form onSubmit={handleUpload} className="p-8 rounded-2xl bg-white border-2 border-dashed border-slate-300 hover:border-brand-400 transition text-center space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center mx-auto">
              <UploadCloud className="w-8 h-8" />
            </div>

            <div className="space-y-1">
              <div className="text-sm font-bold text-slate-800">
                {selectedFile ? selectedFile.name : 'Choose your PDF resume document'}
              </div>
              <p className="text-xs text-slate-400">PDF documents only, maximum file size 5MB</p>
            </div>

            <input
              type="file"
              accept=".pdf,application/pdf"
              id="resume-file-input"
              className="hidden"
              onChange={handleFileChange}
            />

            <div className="flex items-center justify-center gap-3 pt-2">
              <label
                htmlFor="resume-file-input"
                className="px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 font-bold text-xs cursor-pointer transition"
              >
                Browse Files
              </label>

              {selectedFile && (
                <button
                  type="submit"
                  disabled={isUploading}
                  className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs shadow-md shadow-brand-500/20 transition disabled:opacity-60 flex items-center gap-2"
                >
                  {isUploading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Parsing Text...
                    </>
                  ) : (
                    <>
                      Upload & Extract Skills <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              )}
            </div>

            {/* Quick Demo Sample Resumes */}
            <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
              <span className="font-semibold text-slate-600">Quick Test Samples:</span>
              <div className="flex flex-wrap gap-2">
                <a
                  href="/sample_resumes/Rahul_Sharma_Backend_Resume.pdf"
                  download="Rahul_Sharma_Backend_Resume.pdf"
                  className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium inline-flex items-center gap-1 transition"
                  title="Download Rahul Sharma's Backend Developer Resume PDF"
                >
                  <Download className="w-3 h-3 text-slate-500" /> Rahul (Backend)
                </a>
                <a
                  href="/sample_resumes/Sneha_Patel_AI_Resume.pdf"
                  download="Sneha_Patel_AI_Resume.pdf"
                  className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium inline-flex items-center gap-1 transition"
                  title="Download Sneha Patel's AI & Data Science Resume PDF"
                >
                  <Download className="w-3 h-3 text-slate-500" /> Sneha (AI/ML)
                </a>
                <a
                  href="/sample_resumes/Aman_Verma_Web_Resume.pdf"
                  download="Aman_Verma_Web_Resume.pdf"
                  className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium inline-flex items-center gap-1 transition"
                  title="Download Aman Verma's Frontend Web Developer Resume PDF"
                >
                  <Download className="w-3 h-3 text-slate-500" /> Aman (Web)
                </a>
              </div>
            </div>
          </form>

          {/* Extracted Text Snippet */}
          {extractResult && (
            <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-brand-600" /> Extracted Text Preview
                </h3>
                {extractResult.detected_education && (
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 font-bold border border-brand-200">
                    Detected Degree: {extractResult.detected_education}
                  </span>
                )}
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 font-mono text-[11px] text-slate-600 leading-relaxed max-h-40 overflow-y-auto">
                {extractResult.extracted_text_preview}
              </div>
            </div>
          )}
        </div>

        {/* Explainable Human-in-the-loop Review Panel */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-5">
            <div>
              <div className="flex items-center gap-1.5 text-xs font-bold text-brand-600 uppercase tracking-wider mb-1">
                <Sparkles className="w-4 h-4" /> Human Verification
              </div>
              <h2 className="text-sm font-extrabold text-slate-900">Detected Skills Review</h2>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                Per transparency rules, extracted skills require candidate confirmation before updating profile vectors.
              </p>
            </div>

            {!extractResult ? (
              <div className="py-8 text-center text-xs text-slate-400">
                Upload your resume to see detected skill recommendations here.
              </div>
            ) : extractResult.detected_skills.length === 0 ? (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800">
                No known technical skills detected in the parsed text. You can add them manually on your profile page.
              </div>
            ) : (
              <div className="space-y-3">
                <div className="max-h-60 overflow-y-auto space-y-1.5 pr-1">
                  {extractResult.detected_skills.map((skill) => (
                    <label
                      key={skill}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100/70 text-xs cursor-pointer transition"
                    >
                      <span className="font-bold text-slate-800">{skill}</span>
                      <input
                        type="checkbox"
                        checked={selectedSkills.includes(skill)}
                        onChange={() => toggleSkill(skill)}
                        className="rounded text-brand-600 focus:ring-brand-500"
                      />
                    </label>
                  ))}
                </div>

                <button
                  onClick={handleConfirmBatch}
                  disabled={isConfirming || selectedSkills.length === 0}
                  className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm flex items-center justify-center gap-2 transition disabled:opacity-60"
                >
                  <ListPlus className="w-4 h-4" />
                  {isConfirming ? 'Adding Skills...' : `Add (${selectedSkills.length}) Confirmed Skills`}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
