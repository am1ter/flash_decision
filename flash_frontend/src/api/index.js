const MARKETS = [
    {name: 'Bonds', id: '2'},
    {name: 'Commodities', id: '24'},
    {name: 'Currencies', id: '45'},
    {name: 'ETF', id: '28'},
    {name: 'Shares', id: '1'},
    {name: 'USA', id: '25'}
]

// const TICKERS = [
//     {ticker: 'AFLT', name: 'Аэрофлот'},
//     {ticker: 'SBER', name: 'Сбербанк'},
//     {ticker: 'GAZP', name: 'Газпром'},
//     {ticker: 'YNDX', name: 'Яндекс'}
// ]

export function fetchMarkets() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(MARKETS)
        }, 300)
    })
}