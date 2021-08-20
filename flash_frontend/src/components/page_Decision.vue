<template>
    <div>
        <div>Decision</div>
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    export default {
        name: 'page_Decision',
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
