window.AdaptEducaAPI = (() => {
    const BASE = window.ADAPT_EDUCA_API || 'http://127.0.0.1:5000/api';
    const TOKEN_KEY = 'adapteduca_token';

    const getToken = () => { try { return localStorage.getItem(TOKEN_KEY); } catch { return null; } };
    const setToken = token => { try { token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY); } catch {} };

    async function request(path, options = {}) {
        const token = getToken();
        const response = await fetch(`${BASE}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
                ...(options.headers || {})
            }
        });

        const body = await response.json().catch(() => ({}));

        // Sessão expirada ou token inválido: volta para o login.
        if (response.status === 401 && token && !path.startsWith('/auth/')) {
            window.AdaptAuth?.logout();
            throw new Error('Sua sessão expirou. Entre novamente.');
        }

        // O backend responde com { sucesso, mensagem, dados }.
        if (!response.ok || body.sucesso === false) {
            throw new Error(body.mensagem || `Erro HTTP ${response.status}`);
        }

        return body;
    }

    // multipart (upload de PDF): o navegador define o Content-Type com o boundary
    const upload = (path, formData) => {
        const token = getToken();
        return fetch(`${BASE}${path}`, { method: 'POST', body: formData, headers: token ? { Authorization: `Bearer ${token}` } : {} })
            .then(async r => {
                const body = await r.json().catch(() => ({}));
                if (!r.ok || body.sucesso === false) throw new Error(body.mensagem || `Erro HTTP ${r.status}`);
                return body;
            });
    };

    const send = (method, path, data) => request(path, {
        method,
        ...(data !== undefined ? { body: JSON.stringify(data) } : {})
    });

    return {
        base: BASE,
        request,
        getToken,
        setToken,
        health: () => request('/health'),
        get: path => request(path),
        post: (path, data) => send('POST', path, data),
        put: (path, data) => send('PUT', path, data),
        delete: path => send('DELETE', path),
        upload,
        login: data => send('POST', '/auth/login', data),
        register: data => send('POST', '/auth/register', data)
    };
})();
