import { GraphQLClient, gql } from 'graphql-request'

export const client = new GraphQLClient(`${window.location.origin}/submission`)

export type Submission = {
  id: string
  username: string
  label: string
  createdAt: string
}

const SUBMISSIONS_QUERY = gql`
  query Submissions($username: String!) {
    submissions(username: $username) {
      id
      username
      label
      createdAt
    }
  }
`

const CREATE_SUBMISSION = `
  mutation CreateSubmission(
    $username: String!
    $label: String!
    $file: Upload!
  ) {
    createSubmission(username: $username, label: $label, file: $file) {
      id
      label
    }
  }
`

const UPDATE_SUBMISSION = gql`
  mutation UpdateSubmission(
    $username: String!
    $label: String!
    $newLabel: String!
  ) {
    updateSubmission(username: $username, label: $label, newLabel: $newLabel) {
      id
      label
    }
  }
`

const DELETE_SUBMISSION = gql`
  mutation DeleteSubmission($username: String!, $label: String!) {
    deleteSubmission(username: $username, label: $label)
  }
`

const DOWNLOAD_QUERY = gql`
  query Download($username: String!, $label: String!) {
    download(username: $username, label: $label)
  }
`

export async function fetchSubmissions(username: string): Promise<Submission[]> {
  const data = await client.request<{ submissions: Submission[] }>(
    SUBMISSIONS_QUERY,
    { username },
  )
  return data.submissions
}

export async function createSubmission(
  username: string,
  label: string,
  file: File,
): Promise<Submission> {
  const form = new FormData()
  form.append(
    'operations',
    JSON.stringify({
      query: CREATE_SUBMISSION,
      variables: { username, label, file: null },
    }),
  )
  form.append('map', JSON.stringify({ '0': ['variables.file'] }))
  form.append('0', file, file.name)

  const res = await fetch(`${window.location.origin}/submission`, {
    method: 'POST',
    body: form,
  })
  const json = await res.json()
  if (json.errors?.length) throw new Error(json.errors[0].message)
  return json.data.createSubmission as Submission
}

export async function updateSubmission(
  username: string,
  label: string,
  newLabel: string,
): Promise<Submission> {
  const data = await client.request<{ updateSubmission: Submission }>(
    UPDATE_SUBMISSION,
    { username, label, newLabel },
  )
  return data.updateSubmission
}

export async function deleteSubmission(
  username: string,
  label: string,
): Promise<boolean> {
  const data = await client.request<{ deleteSubmission: boolean }>(
    DELETE_SUBMISSION,
    { username, label },
  )
  return data.deleteSubmission
}

export async function downloadUrl(
  username: string,
  label: string,
): Promise<string | null> {
  const data = await client.request<{ download: string | null }>(
    DOWNLOAD_QUERY,
    { username, label },
  )
  return data.download
}