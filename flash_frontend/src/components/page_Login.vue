<template>
    <section id='page'>
        <b-container class="g-0 text-center" fluid>
            <b-row cols="2">
                <b-col class="my-auto" sm="3"><label>Login</label></b-col>
                <b-col class="my-auto" sm="9"><b-form-input id="input-login" placeholder="Enter your login"/></b-col>
                <div class="w-100 my-1"></div>
                <b-col class="my-auto" sm="3"><label>Password</label></b-col>
                <b-col class="my-auto" sm="9"><b-form-input id="input-password" placeholder="Enter your password"/></b-col>
            </b-row>
        </b-container>
    </section>
</template>

<script>
    export default {
        name: 'page_Login'
    }
</script>

<style scoped>
    #page {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        margin: 15px 25px;
        width: auto;
    }
</style>
