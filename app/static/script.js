// Selecione o botão de pesquisa e o campo de entrada
const searchButton = document.getElementById('search-button');
const searchInput = document.querySelector('.search input[type="text"]');

// Adicione um ouvinte de evento ao botão de pesquisa
searchButton.addEventListener('click', () => {
    const searchTerm = searchInput.value;
    // Execute a lógica de pesquisa aqui, por exemplo, redirecione para uma página de resultados
    if (searchTerm) {
        window.location.href = `/search?query=${searchTerm}`;
    }
});
