from factory_component import Rnd, TextEditor
from config import DEV, window_default,dragGrid, resizeGrid, default_debug_msg
from dash import dcc, html, Input, Output, callback, MATCH, ALL, ctx, no_update
import dash
from os import mkdir, rmdir
from os.path import exists
from joblib import dump, load
from shutil import rmtree

class Window:
    __windows = {}
    selected_window_name = ''
    __windows_dir = 'windows'
    DEV = DEV

    def __init__(self,name:str='',code:str=''):
        if name:
            self.__name = name
        else:
            win_names = Window.get().keys()
            for i in range(1,len(Window.get())+2):
                name = f'Window {i}'
                if not name in win_names:
                    self.__name = name
                    break
        self.__code = code
        self.error = ''
        self.__layout = ''
        self.view='editor'
        # small shift on new windows to show the previous one
        self.__default = {**window_default}
        self.__default['x'] += (Window.count() % 6) * resizeGrid[0]
        self.__default['y'] += (Window.count() % 6) * resizeGrid[1]
        self.position = {'x':self.__default['x'],'y':self.__default['y']}
        self.size = {'width':self.__default['width'],'height':self.__default['height']}
        self.__build()

    def __del__(self):
        path = f'{self.__windows_dir}/{self.name.replace(" ","_")}'
        if exists(path):
            rmtree(path)

    def update(self):
        self.__build()
        return self()

    def __call__(self,code:str='',**kwargs):
        if code and code != self.__code:
            self.code = code
        return Rnd(
            children=self.__win_shell(),
            default=self.__default,
            position=self.position,
            size=self.size,
            id={'type':'window-rnd','index':self.name},
            dragHandleClassName='windowHeader',
            dragGrid=dragGrid,
            resizeGrid=resizeGrid,
        )

    def __win_shell(self,*args,**kwargs):
        if not Window.DEV:
            return Window.build_content(self)
        return html.Div([
                html.Div([
                        html.Span(self.name,className='windowHeaderName'),
                        html.Div(className='windowHeaderButton windowCloseButton',id={'type':'window-close-button','index':self.name}),
                    ],
                    id={'type':'window-header','index':self.name},
                    className='windowHeader'
                ),
                html.Div(
                    Window.build_content(self),
                    id={'type':'window-content','index':self.name},
                    className='windowContent'
                ),
                html.Div(
                    Window.build_foot_buttons(self),
                    id={'type':'window-footer','index':self.name},className='windowFooter'
                ),
            ],
            className='windowHandle'
        )
    
    def __build(self):
        self.__layout = ''
        self.error = ''
        # print(self.name,'.__build')
        if self.code:
            try:
                layout = ''
                _locals = locals()
                # layout may change inside self.code
                exec(self.code,globals(),_locals)
                layout = _locals['layout']
                self.__layout = layout
            except Exception as e:
                self.error = str(e)
                print('Error: ',e)
    
    @property
    def layout(self):
        if self.error:
            return ''
        return self.__layout

    @property
    def name(self):
        return self.__name
    
    @property
    def code(self):
        return self.__code
    
    @code.setter
    def code(self,new_code:str):
        self.__code = new_code
        self.__build()
    
    @classmethod
    def add(cls,name:str=''):
        name = '' if name in cls.__windows.keys() else name
        w = Window(name)
        cls.selected_window_name = w.name
        cls.__windows[w.name] = w

    @classmethod
    def get(cls,name:str='',idx:int=None):
        if name == '' and idx == None:
            return cls.__windows
        for win in cls.__windows.values():
            if win.name == name:
                return win
        if len(cls.__windows) > 0:
            idx = -1 if idx is None or idx >= len(cls.__windows) else idx
            return list(cls.__windows.values())[idx]
        return {}

    @classmethod
    def rm(cls,name:str):
        for n in cls.__windows.keys():
            if n == name:
                w = cls.__windows[n]
                del cls.__windows[n]
                cls.selected_window_name = list(cls.__windows.keys())[-1] if len(cls.__windows) > 0 else ''
                return w
        cls.selected_window_name = ''
        return None
    
    @classmethod
    def count(cls):
        return len(cls.__windows.keys())

    @classmethod
    @property
    def names(cls):
        return list(cls.__windows.keys())

    @classmethod
    def build_content(cls,win):
        if not Window.DEV:
            return win.layout
        if win.view == 'editor':
            return TextEditor(value=win.code,id=dict(type='window-text-editor',index=win.name),className='windowTextEditor')
        elif win.view == 'debug':
            return html.Pre(win.error if win.error else default_debug_msg,className='windowDebugError')
        elif win.view == 'result':
            return win.layout
    
    @classmethod
    def build_foot_buttons(cls,win):
        return [
            html.Div(id={'type':'window-btn-editor','index':win.name},className='windowFooterButton windowShowEditorButton ' + ('coded' if win.code else '') + (' selected' if win.view == 'editor' else '')),
            html.Div(id={'type':'window-btn-debug','index':win.name},className='windowFooterButton windowShowDebugButton ' + ('error' if win.error else '') + (' selected' if win.view == 'debug' else '')),
            html.Div(id={'type':'window-btn-result','index':win.name},className='windowFooterButton windowShowResultButton ' + ('available' if win.layout else '') + (' selected' if win.view == 'result' else '')),
        ]

    def save(self):
        path = f'{self.__windows_dir}/{self.name.replace(" ","_")}'
        if not exists(path):
            mkdir(path)
        with open(f'{path}/code.py','w') as fp:
            fp.write(self.code)
        dump(self,f'{path}/state.ckp')

    def load(self):
        fname = f'{self.__windows_dir}/{self.name.replace(" ","_")}/state.ckp'
        if exists(fname):
            win = load(fname)
            self.position = win.position
            self.code = win.code
            self.size = win.size
            self.view = win.view
            self.error = win.error

@callback(
    Output({'type':'window-text-editor','index':MATCH},'value'),
    Input({'type':'window-text-editor','index':MATCH},'value'),
    prevent_initial_call=True,
)
def window_text_editor_value(value):
    win = Window.get(ctx.triggered_id['index'])
    win.code = value
    return value

@callback(
    Output({'type':'window-rnd','index':MATCH},'position'),
    Input({'type':'window-rnd','index':MATCH},'position'),
    prevent_initial_call=True,
)
def window_text_ernd_position(position):
    win = Window.get(ctx.triggered_id['index'])
    win.position = position
    return position

@callback(
    Output({'type':'window-rnd','index':MATCH},'size'),
    Input({'type':'window-rnd','index':MATCH},'size'),
    prevent_initial_call=True,
)
def window_text_ernd_size(size):
    win = Window.get(ctx.triggered_id['index'])
    win.size = size
    return size

@callback(
    Output('store-selected-window-name','data'),
    Input({'type':'window-text-editor','index':ALL},'value'),
    Input({'type':'window-rnd','index':ALL},'position'),
    Input({'type':'window-rnd','index':ALL},'size'),
    Input({'type':'window-content','index':ALL},'n_clicks'),
    Input({'type':'window-header','index':ALL},'n_clicks'),
    Input({'type':'window-footer','index':ALL},'n_clicks'),
    prevent_initial_call=True,
)
def store_selected_window_name_data(value, position, size, n_clicks_content,n_clicks_header,n_clicks_footer):
    if ctx.triggered_id:
        Window.selected_window_name = ctx.triggered_id['index']
    # else:
    #     print(ctx.triggered_id)
    return Window.selected_window_name

@callback(
    Output({'type':'window-footer','index':MATCH},'children'),
    Output({'type':'window-content','index':MATCH},'children'),
    Input({'type':'window-btn-editor','index':MATCH},'n_clicks'),
    Input({'type':'window-btn-debug','index':MATCH},'n_clicks'),
    Input({'type':'window-btn-result','index':MATCH},'n_clicks'),
    prevent_initial_call=True,
)
def window_content_children(b1,b2,b3):
    if ctx.triggered_id is None:
        win = Window.get(Window.selected_window_name)
    else:
        win = Window.get(ctx.triggered_id['index'])
        win.view = ctx.triggered_id['type'].split('-')[-1]
    win.save()
    return Window.build_foot_buttons(win), Window.build_content(win)

if __name__ == '__main__':
    from dash import html
    Window.add('w1')
    w1 = Window.get('w1')
    w1.code='layout=html.Div("Hello World")'
    print(w1.layout)