window.AdaptEducaAPI = (() => {
    const BASE = window.ADAPT_EDUCA_API || 'http://127.0.0.1:5000/api';

    async function request(path, options = {}) {
        const response = await fetch(`${BASE}${path}`, {
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {})
            },
            ...options
        });

        const body = await response.json().catch(() => ({}));

        if (!response.ok || body.success === false) {
            throw new Error(body.message || `Erro HTTP ${response.status}`);
        }

        return body;
    }

    return {
        base: BASE,
        request,
        health: () => request('/status'),
        get: path => request(path),
        post: (path, data) => request(path, {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        put: (path, data) => request(path, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),
        delete: path => request(path, {
            method: 'DELETE'
        }),
        login: data => request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
        register: data => request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        })
    };
})();
