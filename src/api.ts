import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { getReplay, saveReplay } from './replay';

/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI<T>(
  endPoint = '',
  init: RequestInit = {}
): Promise<T> {
  // Make request to Jupyter API
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(
    settings.baseUrl,
    'titanoboa-jupyterlab', // API Namespace
    endPoint
  );

  const replay = getReplay(url);
  if (replay) {
    console.log('Replaying request', url);
    return replay.response as T;
  }

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(url, init, settings);
  } catch (error) {
    throw new ServerConnection.NetworkError(error as any);
  }

  let data: any = await response.text();

  if (data.length > 0) {
    try {
      data = JSON.parse(data);
    } catch (error) {
      console.log('Not a JSON response body.', response);
    }
  }

  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data.message || data);
  }
  saveReplay(url, data);
  return data;
}

/** Stringify data, converting BigInts to strings */
const stringify = (data: unknown) =>
  JSON.stringify(data, (_, v) => (typeof v === 'bigint' ? v.toString() : v));

/**
 * Sends the signature to the server
 * @param token The token to identify the BrowserSigner instance
 * @param data The signature data
 * @returns A promise that resolves when the transaction is sent to the server
 */
export async function sendCallback(token: string, data: unknown) {
  const response = await requestAPI<void>(`callback/${token}`, {
    method: 'POST',
    body: stringify(data)
  });
  console.log(`Sent callback to ${token}`, response);
  return response;
}
