import { useCallback, useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { QRCodeSVG } from 'qrcode.react'
import { Download, Pencil, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  type Submission,
  getSubmissionUrl,
  getSubmissions,
  insertSubmission,
} from '../api'

export default function Dashboard() {
  const { username } = useParams<{ username: string }>()
  const labelInputRef = useRef<HTMLInputElement>(null)

  const [uploadOpen, setUploadOpen] = useState(false)
  const [label, setLabel] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const [entries, setEntries] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedLabel, setSelectedLabel] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [focusTick, setFocusTick] = useState(0)
  const [saving, setSaving] = useState(false)
  const [panelUrl, setPanelUrl] = useState<string | null>(null)
  const [panelUrlLoading, setPanelUrlLoading] = useState(false)

  const selected = entries.find((e) => e.label === selectedLabel) ?? null
  const lastSelected = useRef<Submission | null>(null)
  if (selected) lastSelected.current = selected
  const panelEntry = selected ?? lastSelected.current

  const refetch = useCallback(async () => {
    if (!username) return
    setLoading(true)
    try {
      const data = await getSubmissions(username, 10)
      setEntries(data)
    } catch (err) {
      toast.error(`Failed to load submissions: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setLoading(false)
    }
  }, [username])

  useEffect(() => {
    refetch()
  }, [refetch])

  useEffect(() => {
    if (selected) setDraft(selected.label)
  }, [selected])

  useEffect(() => {
    if (!selected || !username) {
      setPanelUrl(null)
      return
    }
    let cancelled = false
    setPanelUrlLoading(true)
    setPanelUrl(null)
    getSubmissionUrl(username, selected.label)
      .then((url) => {
        if (cancelled) return
        if (!url) {
          toast.error('No download URL returned')
          return
        }
        setPanelUrl(url)
      })
      .catch((err) => {
        if (!cancelled) {
          toast.error(`Failed to get URL: ${err instanceof Error ? err.message : String(err)}`)
        }
      })
      .finally(() => {
        if (!cancelled) setPanelUrlLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [selected, username])

  useEffect(() => {
    if (focusTick > 0) labelInputRef.current?.focus()
  }, [focusTick])

  const openEntry = (entry: Submission) => setSelectedLabel(entry.label)
  const editEntry = (entry: Submission) => {
    setSelectedLabel(entry.label)
    setFocusTick((t) => t + 1)
  }
  const downloadEntry = async (_entry: Submission) => {
    toast.info('Download not wired up yet')
  }
  const deleteEntry = async (_entry: Submission) => {
    toast.info('Delete not wired up yet')
  }
  const saveLabel = async () => {
    if (!selected) return
    const next = draft.trim()
    if (!next) {
      toast.error('Label cannot be empty')
      return
    }
    if (next === selected.label) {
      toast.info('No changes to save')
      return
    }
    setSaving(true)
    toast.info('Update not wired up yet')
    setSaving(false)
  }

  const openDialog = () => setUploadOpen(true)
  const closeDialog = () => {
    setUploadOpen(false)
    setLabel('')
    setFile(null)
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username) return
    const trimmed = label.trim()
    if (!trimmed) {
      toast.error('Label is required')
      return
    }
    if (!file) {
      toast.error('CSV file is required')
      return
    }
    setSubmitting(true)
    try {
      await insertSubmission(username, trimmed, file)
      toast.success(`Uploaded "${trimmed}"`)
      closeDialog()
      await refetch()
    } catch (err) {
      toast.error(`Upload failed: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-neutral-900">
          {username}'s dashboard
        </h1>
        <button
          onClick={openDialog}
          className="px-3 py-2 rounded bg-violet-600 text-white font-medium hover:bg-violet-700"
        >
          Upload
        </button>
      </div>

      {loading ? (
        <p className="mt-6 text-neutral-500">Loading...</p>
      ) : entries.length === 0 ? (
        <p className="mt-6 text-neutral-500">No submissions yet.</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-2">
          {entries.map((entry) => (
            <li key={entry.label}>
              <div
                className={`flex items-center gap-2 px-4 py-3 rounded border transition ${
                  selectedLabel === entry.label
                    ? 'border-violet-500 bg-violet-50'
                    : 'border-neutral-200 hover:bg-neutral-50'
                }`}
              >
                <button
                  onClick={() => openEntry(entry)}
                  className="flex-1 text-left"
                >
                  {entry.label}
                </button>
                <button
                  onClick={() => downloadEntry(entry)}
                  aria-label="Download"
                  className="p-1.5 rounded text-neutral-500 hover:bg-neutral-200 hover:text-neutral-800"
                >
                  <Download size={16} />
                </button>
                <button
                  onClick={() => editEntry(entry)}
                  aria-label="Edit"
                  className="p-1.5 rounded text-neutral-500 hover:bg-neutral-200 hover:text-neutral-800"
                >
                  <Pencil size={16} />
                </button>
                <button
                  onClick={() => deleteEntry(entry)}
                  aria-label="Delete"
                  className="p-1.5 rounded text-neutral-500 hover:bg-red-100 hover:text-red-600"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div
        className={`fixed inset-0 z-40 ${selected ? '' : 'pointer-events-none'}`}
        onClick={() => setSelectedLabel(null)}
      >
        <aside
          onClick={(e) => e.stopPropagation()}
          className={`absolute top-0 right-0 h-full w-96 bg-white border-l border-neutral-200 shadow-xl p-8 flex flex-col gap-4 transition-transform duration-300 ease-out ${
            selected ? 'translate-x-0' : 'translate-x-full'
          }`}
        >
          {panelEntry && (
            <>
              <div className="self-center h-[240px] w-[240px] flex items-center justify-center">
                {panelUrlLoading ? (
                  <span className="text-sm text-neutral-500">Loading QR...</span>
                ) : panelUrl ? (
                  <QRCodeSVG value={panelUrl} size={240} />
                ) : (
                  <span className="text-sm text-neutral-500">No URL</span>
                )}
              </div>
              <label className="flex flex-col gap-1 text-sm text-neutral-700">
                Label
                <input
                  ref={labelInputRef}
                  type="text"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  className="px-3 py-2 rounded border border-neutral-300 focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
              </label>
              <button
                onClick={saveLabel}
                disabled={saving}
                className="px-3 py-2 rounded bg-violet-600 text-white font-medium hover:bg-violet-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </>
          )}
        </aside>
      </div>

      {uploadOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 flex items-center justify-center"
          onClick={closeDialog}
        >
          <form
            onSubmit={submit}
            onClick={(e) => e.stopPropagation()}
            className="w-96 flex flex-col gap-4 p-6 bg-white rounded-lg shadow-xl"
          >
            <h2 className="text-lg font-semibold text-neutral-900">Upload file</h2>
            <label className="flex flex-col gap-1 text-sm text-neutral-700">
              Label
              <input
                type="text"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                className="px-3 py-2 rounded border border-neutral-300 focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </label>
            <div className="flex flex-col gap-1 text-sm text-neutral-700">
              CSV File:
              <input
                id="csv-input"
                type="file"
                accept=".csv,text/csv"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="hidden"
              />
              <label
                htmlFor="csv-input"
                className="px-3 py-2 rounded border border-neutral-300 cursor-pointer hover:bg-neutral-50"
              >
                {file ? file.name : 'Click to choose'}
              </label>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={closeDialog}
                className="px-3 py-2 rounded border border-neutral-300 text-neutral-700 hover:bg-neutral-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-3 py-2 rounded bg-violet-600 text-white font-medium hover:bg-violet-700 disabled:opacity-50"
              >
                {submitting ? 'Uploading...' : 'Submit'}
              </button>
            </div>
          </form>
        </div>
      )}
    </main>
  )
}