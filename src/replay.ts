

/**
 * We cache the responses to avoid making the same request twice.
 * The requests generally will fail because the server invalidates the tokens.
 * We store the responses in localStorage to avoid errors reloading the page.
 */
type Replay = {url: string, initJson: string, response: unknown};
const replays: Replay[] = localStorage.getItem("replays") ? JSON.parse(localStorage.getItem("replays")!) : [];
const MAX_REPLAYS = 100;

export const getReplay = (url: string, initJson: string) => replays.find(r => r.url === url && r.initJson === initJson);

export function saveReplay(requestUrl: string, initJson: string, data: any) {
  replays.push({ url: requestUrl, initJson, response: data });
  if (replays.length > MAX_REPLAYS) {
    replays.shift();
  }
  localStorage.setItem("replays", JSON.stringify(replays));
}
