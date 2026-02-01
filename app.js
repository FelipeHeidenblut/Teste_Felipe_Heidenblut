new Vue({
  el: '#app',
  data: {
    apiBase: 'http://localhost:8000',
    operadoras: [],
    page: 1,
    limit: 10,
    total: 0,
    search: '',
    detalhe: null,
    historico: [],
    estatisticas: null
  },
  mounted() {
    this.carregarOperadoras(1);
  },
  methods: {
    carregarOperadoras(page) {
      this.page = page;
      const params = { page: this.page, limit: this.limit };
      if (this.search) {
        params.q = this.search;
      }
      axios.get(this.apiBase + '/api/operadoras', { params })
        .then(res => {
          this.operadoras = res.data.data;
          this.total = res.data.total;
        })
        .catch(err => {
          console.error(err);
          this.operadoras = [];
        });
    },
    verDetalhes(cnpj) {
      this.detalhe = null;
      this.historico = [];

      axios.get(this.apiBase + '/api/operadoras/' + cnpj)
        .then(res => {
          this.detalhe = res.data;
        })
        .catch(err => {
          console.error(err);
        });

      axios.get(this.apiBase + '/api/operadoras/' + cnpj + '/despesas')
        .then(res => {
          this.historico = res.data.historico;
        })
        .catch(err => {
          console.error(err);
        });
    },
    carregarEstatisticas() {
      axios.get(this.apiBase + '/api/estatisticas')
        .then(res => {
          this.estatisticas = res.data;
        })
        .catch(err => {
          console.error(err);
        });
    }
  }
});
