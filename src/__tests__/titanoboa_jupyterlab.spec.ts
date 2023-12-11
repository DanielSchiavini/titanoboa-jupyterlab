/**
 * Example of [Jest](https://jestjs.io/docs/getting-started) unit tests
 */

import plugin from '../index';

describe('titanoboa-jupyterlab-extension', () => {
  beforeEach(() => {
    window._titanoboa = undefined;
    plugin.activate({} as any);
  });

  it('should inject callbacks', () => {
    expect(window._titanoboa).toEqual({
      loadSigner: expect.any(Function),
      signTransaction: expect.any(Function)
    })
  });
});
