<template>
    <div id="header-layout" v-if="isAuth == true">
        <div id="header-left">
            <div class="header-button">
                <img class="header-icon-left" src="../assets/icons/i_header_user.svg"/>
                <p class="header-text-left">{{ user.email }}</p>
            </div>
        </div>
        <div id="header-right">
            <a id="button-logout" class="header-button" v-on:click="logout()">
                <img class="header-icon-right" src="../assets/icons/i_header_logout.svg"/>
                <p class="header-text-right">logout</p>
            </a>
        </div>
    </div>
</template>

<script>
    import { mapState, mapMutations } from "vuex"

    export default {
        name: "Header",
        props: {},
        computed: {
            ...mapState(["user"]),
            isAuth() {
                return this.$store.getters.isAuth
            }
        },
        methods: {
            ...mapMutations(["setNoUser"]),
            logout() {
                this.$store.commit("setNoUser")
                // Go to the login page
                this.$router.push("/login/")
            }
        }
}
</script>

<style>
    #header-layout {
        display: flex;
        flex-direction: row;
        width: 100%;
        margin: 0px 0px;
        height: 35px;
    }

    #header-left {
        width: 50%;
        text-align: left;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
    }

    #header-right {
        width: 50%;
        text-align: right;
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
        align-items: center;
    }

    .header-button {
        display: flex;
        flex-direction: row;
        cursor: pointer;
    }

    .header-icon-left {
        margin: 0px 0px 0px 5px;
    }

    .header-icon-right {
        margin: 0px 5px 0px 0px;
    }

    .header-text-left {
        margin: 0px auto;
        padding: 0px 0px 0px 5px;
    }

    .header-text-right {
        margin: 0px auto;
        padding: 0px 5px 0px 0px;
    }

</style>