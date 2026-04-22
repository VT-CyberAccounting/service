import { GraphQLClient, gql } from 'graphql-request'

export const client = new GraphQLClient(`${window.location.origin}/submission`)

export type Submission = {
  label: string
  createdAt: string
}

const GET_SUBMISSIONS = gql`
  query GetSubmissions($username: String!, $limit: Int!) {
    getSubmission(username: $username, limit: $limit) {
      label
      createdAt
    }
  }
`

export async function getSubmissions(
  username: string,
  limit = 10,
): Promise<Submission[]> {
  const data = await client.request<{ getSubmission: Submission[] }>(
    GET_SUBMISSIONS,
    { username, limit },
  )
  return data.getSubmission
}

const GET_SUBMISSION_URL = gql`
  query GetSubmissionUrl($username: String!, $label: String!) {
    getSubmission(username: $username, label: $label, limit: 1) {
      url
    }
  }
`

export async function getSubmissionUrl(
  username: string,
  label: string,
): Promise<string | null> {
  const data = await client.request<{ getSubmission: { url: string | null }[] }>(
    GET_SUBMISSION_URL,
    { username, label },
  )
  return data.getSubmission[0]?.url ?? null
}

const INSERT_SUBMISSION = gql`
  mutation InsertSubmission($username: String!, $label: String!) {
    insertSubmission(username: $username, label: $label)
  }
`

export async function insertSubmission(
  username: string,
  label: string,
  file: File,
): Promise<void> {
  const data = await client.request<{ insertSubmission: string }>(
    INSERT_SUBMISSION,
    { username, label },
  )
  const res = await fetch(data.insertSubmission, {
    method: 'PUT',
    body: file,
  })
  if (!res.ok) throw new Error(`Upload failed: ${res.status} ${res.statusText}`)
}
