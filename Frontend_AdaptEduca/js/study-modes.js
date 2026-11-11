
(function () {
    "use strict";

    document.addEventListener(
        "DOMContentLoaded",
        iniciarModosEstudo
    );

    async function iniciarModosEstudo() {

        const modos = Array.from(
            document.querySelectorAll(
                '.mode-grid input[name="mode"]'
            )
        );

        const botao = document.getElementById(
            "saveStudyModes"
        );

        const mensagem = document.getElementById(
            "studyModesMessage"
        );

        if (!modos.length || !botao) {
            return;
        }

        const api = window.AdaptEducaAPI;
        const auth = window.AdaptAuth;

        // Atualizar visual dos cartões.
        function atualizarVisual() {

            modos.forEach(function (input) {

                const card = input.closest(
                    ".select-card"
                );

                if (!card) {
                    return;
                }

                card.classList.toggle(
                    "selected",
                    input.checked
                );

            });
        }

        // Apresentar mensagens.
        function avisar(texto, erro = false) {

            if (!mensagem) {
                return;
            }

            mensagem.textContent = texto;

            mensagem.style.color = erro
                ? "#f87171"
                : "var(--text-2)";
        }

        // Obter escolhas marcadas.
        function obterSelecionados() {

            return modos
                .filter(input => input.checked)
                .map(input => input.value);
        }

        // Atualizar ao selecionar/desmarcar.
        modos.forEach(function (input) {

            input.addEventListener(
                "change",
                atualizarVisual
            );

        });

        atualizarVisual();

        // Verificar autenticação.
        const usuario = auth?.session();

        if (
            !usuario ||
            usuario.role !== "aluno" ||
            !api?.getToken()
        ) {

            avisar(
                "Entre com uma conta de aluno " +
                "para salvar os modos no seu perfil."
            );

            botao.addEventListener(
                "click",
                function () {
                    avisar(
                        "Faça login como aluno primeiro.",
                        true
                    );
                }
            );

            return;
        }

        // ==================================
        // CARREGAR MODOS DO BANCO
        // ==================================

        try {

            const resposta = await api.get(
                "/alunos/me/modos-estudo"
            );

            const salvos = resposta.dados?.modos;

            if (Array.isArray(salvos)) {

                modos.forEach(function (input) {

                    input.checked = salvos.includes(
                        input.value
                    );

                });

                atualizarVisual();
            }

        } catch (erro) {

            console.error(
                "Erro ao carregar modos:",
                erro
            );

            avisar(
                "Não foi possível carregar " +
                "os modos salvos.",
                true
            );
        }

        // ==================================
        // SALVAR MODOS NO MYSQL
        // ==================================

        botao.addEventListener(
            "click",
            async function () {

                const selecionados =
                    obterSelecionados();

                botao.disabled = true;

                avisar("Salvando suas preferências...");

                try {

                    const resposta = await api.put(
                        "/alunos/me/modos-estudo",
                        {
                            modos: selecionados
                        }
                    );

                    if (resposta.sucesso !== true) {
                        throw new Error(
                            "Falha ao salvar os modos."
                        );
                    }

                    avisar(
                        "Modos salvos com sucesso " +
                        "no seu perfil!"
                    );

                    window.showToast?.(
                        "Modos de estudo salvos!",
                        "success"
                    );

                } catch (erro) {

                    console.error(
                        "Erro ao salvar:",
                        erro
                    );

                    avisar(
                        erro.message ||
                        "Não foi possível salvar.",
                        true
                    );

                } finally {

                    botao.disabled = false;
                }

            }
        );
    }

})();
