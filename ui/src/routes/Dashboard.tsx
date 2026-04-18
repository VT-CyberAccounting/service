import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { QRCodeSVG } from 'qrcode.react'
import { Pencil, Trash2 } from 'lucide-react'
import { toast } from 'sonner'

type Entry = { label: string; uuid: string }

export default function Dashboard() {
  const { username } = useParams<{ username: string }>()
  const labelInputRef = useRef<HTMLInputElement>(null)

  const [uploadOpen, setUploadOpen] = useState(false)
  const [label, setLabel] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [entries, setEntries] = useState<Entry[]>([
    { label: 'Placeholder entry', uuid: crypto.randomUUID() },
  ])
  const [selectedUuid, setSelectedUuid] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [focusTick, setFocusTick] = useState(0)

  const selected = entries.find((e) => e.uuid === selectedUuid) ?? null
  const lastSelected = useRef<Entry | null>(null)
  if (selected) lastSelected.current = selected
  const panelEntry = selected ?? lastSelected.current

  useEffect(() => {
    if (selected) setDraft(selected.label)
  }, [selected])

  useEffect(() => {
    if (focusTick > 0) labelInputRef.current?.focus()
  }, [focusTick])

  const openEntry = (entry: Entry) => setSelectedUuid(entry.uuid)
  const editEntry = (entry: Entry) => {
    setSelectedUuid(entry.uuid)
    setFocusTick((t) => t + 1)
  }
  const deleteEntry = (uuid: string) => {
    const target = entries.find((e) => e.uuid === uuid)
    setEntries((prev) => prev.filter((e) => e.uuid !== uuid))
    if (selectedUuid === uuid) setSelectedUuid(null)
    if (target) toast.success(`Deleted "${target.label}"`)
  }
  const saveLabel = () => {
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
    setEntries((prev) =>
      prev.map((e) => (e.uuid === selected.uuid ? { ...e, label: next } : e)),
    )
    toast.success('Label updated')
  }

  const openDialog = () => setUploadOpen(true)
  const closeDialog = () => {
    setUploadOpen(false)
    setLabel('')
    setFile(null)
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!label.trim()) {
      toast.error('Label is required')
      return
    }
    if (!file) {
      toast.error('CSV file is required')
      return
    }
    toast.success(`Uploaded "${label.trim()}"`)
    closeDialog()
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

      <ul className="mt-6 flex flex-col gap-2">
        {entries.map((entry) => (
          <li key={entry.uuid}>
            <div
              className={`flex items-center gap-2 px-4 py-3 rounded border transition ${
                selectedUuid === entry.uuid
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
                onClick={() => editEntry(entry)}
                aria-label="Edit"
                className="p-1.5 rounded text-neutral-500 hover:bg-neutral-200 hover:text-neutral-800"
              >
                <Pencil size={16} />
              </button>
              <button
                onClick={() => deleteEntry(entry.uuid)}
                aria-label="Delete"
                className="p-1.5 rounded text-neutral-500 hover:bg-red-100 hover:text-red-600"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div
        className={`fixed inset-0 z-40 ${selected ? '' : 'pointer-events-none'}`}
        onClick={() => setSelectedUuid(null)}
      >
        <aside
          onClick={(e) => e.stopPropagation()}
          className={`absolute top-0 right-0 h-full w-96 bg-white border-l border-neutral-200 shadow-xl p-8 flex flex-col gap-4 transition-transform duration-300 ease-out ${
            selected ? 'translate-x-0' : 'translate-x-full'
          }`}
        >
          {panelEntry && (
            <>
              <div className="self-center">
                <QRCodeSVG value={panelEntry.uuid} size={240} />
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
                className="px-3 py-2 rounded bg-violet-600 text-white font-medium hover:bg-violet-700"
              >
                Save
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
          <label className="flex flex-col gap-1 text-sm text-neutral-700">
            CSV file
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="text-sm"
            />
          </label>
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
              className="px-3 py-2 rounded bg-violet-600 text-white font-medium hover:bg-violet-700"
            >
              Submit
            </button>
          </div>
          </form>
        </div>
      )}
    </main>
  )
}