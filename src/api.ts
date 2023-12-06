import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { TransactionResponse } from 'ethers';
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
  const requestUrl = URLExt.join(
    settings.baseUrl,
    'titanoboa-jupyterlab', // API Namespace
    endPoint
  );

  const initJson = JSON.stringify(init);
  const replay = getReplay(requestUrl, initJson);
  if (replay) {
    return replay.response as T;
  }

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
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
  saveReplay(requestUrl, initJson, data);
  return data;
}

/** Stringify data, converting BigInts to strings */
const stringify = (data: unknown) => JSON.stringify(data, (_, v) => typeof v === 'bigint' ? v.toString() : v);

/**
 * Sends the signature to the server
 * @param token The token to identify the BrowserSigner instance
 * @param response The transaction details
 * @returns A promise that resolves when the transaction is sent to the server
 */
export function sendTransaction(token: string, response: TransactionResponse) {
  return requestAPI<void>('send_transaction', {
    method: 'POST',
    body: stringify({ ...response, token })
  });
}

/**
 * Sets the signer for the given token
 * @param token The token to identify the BrowserSigner instance
 * @param address The address of the signer
 */
export function setSigner(token: string, address: string) {
  return requestAPI<void>('set_signer', {
    method: 'POST',
    body: JSON.stringify({ address, token })
  });
}
