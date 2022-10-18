import dash
from dash import html, dcc, Input, State, Output, ctx, ALL
from components import Window
from config import DEV, window_default
from factory_component import Rnd, TextEditor

app = dash.Dash(__name__)

app.layout = html.Div([
        html.Div(
            id='workspace',
            className='workspace'
        ),
        html.Div([
                html.Button('▶',id='swap-dev-button'),
                html.Button('+',id='add-window-button'),
            ],
            id='dev-menu',
            className='devMenu'
        )
    ],
    id='app',
)

@app.callback(
    Output('swap-dev-button','children'),
    Input('swap-dev-button','n_clicks'),
)
def swap_dev_button_children(_):
    global DEV
    DEV = not DEV
    return '▶️' if DEV else '⏸'

@app.callback(
    Output('workspace','children'),
    Input('swap-dev-button','children'),
    Input('add-window-button','n_clicks'),
    prevent_initial_call=True
)
def workspace_children(btn1,btn2):
    global DEV
    print('Chamou ',ctx.triggered_id)
    if ctx.triggered_id == 'add-window-button':
        Window.add()
        print('Criou')
    return [w(dev=DEV) for w in Window.get().values()]

if __name__ == '__main__':
    app.run(debug=True)