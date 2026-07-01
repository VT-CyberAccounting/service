export default function Login() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="w-80 flex flex-col gap-4 p-8 rounded-lg border border-neutral-200 bg-white shadow-sm text-center">
        <p className="text-neutral-900">
          <a
            href="/auth/login"
            className="text-violet-600 font-medium hover:underline"
          >
            login
          </a>{' '}
          to continue
        </p>
      </div>
    </main>
  )
}