<template>
    <div id='header_layout' v-if='isAuth == true'>
        <div id='header_left'>
            <div class='header_button'>
                <img class='header_icon_left' src='../assets/icons/i_header_user.svg'/>
                <p class='header_text_left'>{{ user.email }}</p>
            </div>
        </div>
        <div id='header_right'>
            <a id='button-logout' class='header_button' v-on:click="logout()">
                <img class='header_icon_right' src='../assets/icons/i_header_logout.svg'/>
                <p class='header_text_right'>logout</p>
            </a>
        </div>
    </div>
</template>

<script>
    import { mapState, mapMutations } from 'vuex'

    export default {
        name: 'Header',
        props: {},
        computed: {
            ...mapState(['user']),
            isAuth() {
                return this.$store.getters.isAuth
            }
        },
        methods: {
            ...mapMutations(['setNoUser']),
            logout() {
                this.$store.commit('setNoUser')
                // Go to the login page
                this.$router.push('/sign-in/')
            }
        }
}
</script>

<style>
    #header_layout {
        display: flex;
        flex-direction: row;
        width: 100%;
        margin: 0px 0px;
        height: 35px;
    }

    #header_left {
        width: 50%;
        text-align: left;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
    }

    #header_right {
        width: 50%;
        text-align: right;
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
        align-items: center;
    }

    .header_button {
        display: flex;
        flex-direction: row;
        cursor: pointer;
    }

    .header_icon_left {
        margin: 0px 0px 0px 5px;
    }

    .header_icon_right {
        margin: 0px 5px 0px 0px;
    }

    .header_text_left {
        margin: 0px auto;
        padding: 0px 0px 0px 5px;
    }

    .header_text_right {
        margin: 0px auto;
        padding: 0px 5px 0px 0px;
    }

</style>