import { GraphQLClient, gql } from 'graphql-request'

export const client = new GraphQLClient(`${window.location.origin}/api/submission`)

export async function isAuthenticated(): Promise<boolean> {
  const res = await fetch(`${window.location.origin}/auth/whoami`, {
    credentials: 'include',
  })
  return res.ok
}

export type Submission = {
  label: string
  createdAt: string
}

const GET_SUBMISSIONS = gql`
  query GetSubmissions($limit: Int!) {
    getSubmission(limit: $limit) {
      label
      createdAt
    }
  }
`

export async function getSubmissions(limit = 10): Promise<Submission[]> {
  const data = await client.request<{ getSubmission: Submission[] }>(
    GET_SUBMISSIONS,
    { limit },
  )
  return data.getSubmission
}

const GET_SUBMISSION_URL = gql`
  query GetSubmissionUrl($label: String!) {
    getSubmission(label: $label, limit: 1) {
      url
    }
  }
`

export async function getSubmissionUrl(
  label: string,
): Promise<string | null> {
  const data = await client.request<{ getSubmission: { url: string | null }[] }>(
    GET_SUBMISSION_URL,
    { label },
  )
  return data.getSubmission[0]?.url ?? null
}

const INSERT_SUBMISSION = gql`
  mutation InsertSubmission($label: String!) {
    insertSubmission(label: $label)
  }
`

export async function insertSubmission(
  label: string,
  file: File,
): Promise<void> {
  const data = await client.request<{ insertSubmission: string }>(
    INSERT_SUBMISSION,
    { label },
  )
  const res = await fetch(data.insertSubmission, {
    method: 'PUT',
    body: file,
  })
  if (!res.ok) throw new Error(`Upload failed: ${res.status} ${res.statusText}`)
}

const RENAME_SUBMISSION = gql`
  mutation RenameSubmission($label: String!, $newLabel: String!) {
    renameSubmission(label: $label, newLabel: $newLabel)
  }
`

export async function renameSubmission(
  label: string,
  newLabel: string,
): Promise<void> {
  await client.request(RENAME_SUBMISSION, { label, newLabel })
}

const DELETE_SUBMISSION = gql`
  mutation DeleteSubmission($label: String!) {
    deleteSubmission(label: $label)
  }
`

export async function deleteSubmission(label: string): Promise<void> {
  await client.request(DELETE_SUBMISSION, { label })
}

export type DeviceStatus = 'initiated' | 'redeemed' | 'approved' | 'delivered'

export async function createDevicePairing(): Promise<string> {
  const res = await fetch(`${window.location.origin}/auth/device`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) throw new Error(`Failed to start pairing: ${res.status} ${res.statusText}`)
  const data = (await res.json()) as { token: string }
  return data.token
}

export async function getDeviceStatus(pairingToken: string): Promise<DeviceStatus> {
  const res = await fetch(
    `${window.location.origin}/auth/device/status?pairing_token=${encodeURIComponent(pairingToken)}`,
    { credentials: 'include' },
  )
  if (!res.ok) throw new Error(`Status check failed: ${res.status} ${res.statusText}`)
  const data = (await res.json()) as { status: DeviceStatus }
  return data.status
}

export async function approveDevice(pairingToken: string, code: string): Promise<void> {
  const res = await fetch(
    `${window.location.origin}/auth/device/approve?pairing_token=${encodeURIComponent(
      pairingToken,
    )}&code=${encodeURIComponent(code)}`,
    { method: 'POST', credentials: 'include' },
  )
  if (!res.ok) {
    const detail = (await res.json().catch(() => null)) as { detail?: string } | null
    throw new Error(detail?.detail ?? `Approve failed: ${res.status} ${res.statusText}`)
  }
}
