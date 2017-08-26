import kivy
from kivy.app import App
from kivy.config import Config

kivy.require("1.10.0")
Config.read("mitc.ini")

from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout

INPUT_REFERENCE = 0

class Input(TextInput):
    """
    Class responsável pelo Input e suas caracteristicas.

    pontuation : sinaliza se o texto já foi pontuado ou não
    text_float :  variável usada nas operações matemáticas
    allowed_characters : caracteres permitidos no software
    first_float : boolean que sinaliza se o número do input já foi tratado
    """

    pontuation = False
    first_float = True
    text_float = 0

    def __init__(self, **kwargs):
        super(Input, self).__init__(**kwargs)
        global INPUT_REFERENCE
        INPUT_REFERENCE = self
        self.size_hint = (1,0.25)
        padding_height = (self.height - self.line_height)/2
        self.multiline = False
        self.font_size = "32sp"
        self.text = ""
        self.background_normal = ""
        self.background_active = ""
        self.background_color = (1, 1, 1, 1)
        self.cursor_color = (0, 0, 0, 1)
        self.padding = (5, padding_height)
        self.readonly = True
    
    def on_text(self, instance, text):
        """
        Evento responsável por qualquer modificação do texto do input, além 
        de ser responsável pelas pontuações e verificações
        """

        if self.first_float and instance.text != "": 
            self.text_float = float(instance.text)
            self.first_float = False
        elif not self.first_float and instance.text != "":
            self.text_float = float(instance.text.replace(".", "").replace(",", "."))
        else:
            self.text_float = float("0") 

        if not self.pontuation:
            text = str(self.text_float).replace(".", ",")
            if len(text) > 3:
                pre_text = ""
                count = 0
                before_virg = text.find(",")
                for number in list(text)[:before_virg][::-1]:
                    pre_text += number
                    count += 1
                    if count == 3:
                        pre_text += "."
                        count = 0
                self.pontuation = True
                if text[before_virg:] != ",0":
                    pre_text = "{}{}".format(pre_text[::-1], text[before_virg:])
                else:
                    pre_text = pre_text[::-1]
                instance.text = pre_text[1:] if pre_text[0] == "." else pre_text   

        self.pontuation = False

class CalcButton(Button):
    """
    Classe padrão para todos os botões da calculadora
    """

    def __init__(self, **kwargs):
        super(CalcButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.size_hint_y = 0.15
        self.font_size = "27sp"
        self.background_color = (41/255, 128/255, 185/255,1.0)
        self.background_down = "images/texture_press.png"

class Main_layout(StackLayout):
    """
    Layout principal da calculadora, organiza toda a estrutura básica
    da calculadora

    buttons_instances : dicionário de todas as instâncias dos botões usados
    key_operation_reference : dicionário que relaciona um botão a uma tecla
    class_operation : instância da classe que irá tratar as operações
    """


    buttons_instances = {}
    key_operation_reference = {
        "C" : ("backspace", ""),
        "+" : ("=", "shift"),
        "-" : ("-", ""),
        "*" : ("8", "shift"),
        "÷" : ("q", "alt"),
        "%" : ("5", "shift"),
        "^" : (1073741824, "shift"),
        "=" : ("enter", "")
    }

    def __init__(self, **kwargs):
        super(Main_layout, self).__init__(**kwargs)

        my_keyboard = Window.request_keyboard(None, None)
        my_keyboard.bind(on_key_down=self.on_key_down)

        self.add_widget(Input())
        self.class_operation = OperationsFunctions()

        operations_button = {
            "C": self.class_operation.clean, 
            "^" : self.class_operation.potentiation, 
            "%" : self.class_operation.percentage, 
            "+" : self.class_operation.sum
        }
        self.add_buttons(operations_button, orientation="horizontal")

        alfa_numbers_layout = StackLayout(orientation="rl-tb")
        alfa_numbers_layout.size_hint_x = 0.75
        for number in range(9, 0, -1):
            btn_alfa = CalcButton()
            btn_alfa.size_hint_x = 1/3
            btn_alfa.text = str(number)
            self.buttons_instances[btn_alfa.text] = btn_alfa
            btn_alfa.bind(on_press=self.numbers_insert)
            alfa_numbers_layout.add_widget(btn_alfa)
        
        alfa_virg = CalcButton(
            text = ",", 
            size_hint_x=1/3, 
            on_press=self.numbers_insert)  
        self.buttons_instances[","] = alfa_virg
        alfa_numbers_layout.add_widget(alfa_virg)

        alfa_zero = CalcButton(
            text = "0",  
            size_hint_x=2/3, 
            on_press=self.numbers_insert)
        self.buttons_instances["0"] = alfa_zero
        alfa_numbers_layout.add_widget(alfa_zero)

        self.add_widget(alfa_numbers_layout)

        operations_button = {
            "-": self.class_operation.decrease,
            "*": self.class_operation.multiplication,
            "÷": self.class_operation.division,
            "=": self.class_operation.equal
        }

        self.add_buttons(operations_button, orientation="vertical")


    def add_buttons(self, operations_dict={},  orientation="horizontal"):
        """
        Metódo que adiciona vários botões de uma vez, baseado na orientação desejada
        """

        if operations_dict != {} and orientation == "horizontal":
            layout = False
            width_button = 1/len(operations_dict)
        elif orientation == "vertical":
            layout = StackLayout()
            layout.size_hint_x = 0.25
            width_button = 1

        for text_put, function in operations_dict.items():
            button = CalcButton(text=str(text_put))
            self.buttons_instances[button.text] = button
            button.bind(on_press=function)
            button.size_hint_x = width_button
            if layout != False: layout.add_widget(button)
            else : self.add_widget(button)
        else:
            if layout != False: self.add_widget(layout)

    def numbers_insert(self, button_instance):
        """
        Metódo que adiciona ao input os valores dos botões númericos

        button_instance: instância do botão
        """

        self.class_operation.insert_anything(button_instance.text)

    def on_key_down(self, instance, keycode, text, modifiers):
        """
        Evento responsável pela checagem das teclas pressionadas,
        relacionando-as seus respectivos botões

        instance :  instância do teclado
        keycode : (ansii_key, key)
        text : text_key
        modifiers : sub_keys
        """

        modifiers.append("")

        for btn_text, key in self.key_operation_reference.items():
            if key[0] in keycode and modifiers[0].find(key[1]) != -1:
                self.buttons_instances[btn_text].trigger_action(duration=0.15)
                return True
         
        if keycode[1] in self.buttons_instances:
            self.buttons_instances[keycode[1]].trigger_action(duration=0.15)

        self.class_operation.local_input.do_cursor_movement("cursor_end")


class OperationsFunctions:
    """
    Class responsável por todas as operações matemáticas disponíveis na calculadora

    newest_operation : instância da operação mais recente
    local_input : variável local que faz referência ao input
    ans : último valor resultante
    code_error : dicionário de erros e suas mensagens
    """

    newest_operation = None

    def __init__(self):
        global INPUT_REFERENCE
        self.local_input = INPUT_REFERENCE
        self.ans = []

    def clean(self, *args):
        """
        Limpa o input
        """
        self.local_input.text = ""

    def generic_operation(self, operation_newest):
        """
        Operação genérica, equivalente a um intermediário entre a requisição
        e a operação

        operation_newest : instância da operação que a chamou
        """

        if self.ans == []:
            self.ans.append(self.local_input.text_float)
            self.newest_operation = operation_newest
            self.clean()
        else:
            self.local_input.first_float = True
            self.local_input.text = self.newest_operation(
                self.ans[0], 
                self.local_input.text_float)
            self.ans = []
        
    def potentiation(self, *args):
        if type(args[0]) != float:        
            self.generic_operation(self.potentiation)
        else:
            return str(args[0] ** args[1])

    def percentage(self, *args):
        if type(args[0]) != float:        
            self.generic_operation(self.percentage)
        else:
            return str((args[0] * args[1]) // 100) 

    def sum(self, *args):
        if type(args[0]) != float:        
            self.generic_operation(self.sum)
        else:
            return str(args[0] + args[1]) 

    def decrease(self, *args):
        if type(args[0]) != float:        
            self.generic_operation(self.decrease)
        else:
            return str(args[0] - args[1]) 

    def multiplication(self, *args):
        if type(args[0]) != float:        
            self.generic_operation(self.multiplication)
        else:
            return str(args[0] * args[1]) 

    def division(self, *args):
        if type(args[0]) != float:        
            self.generic_operation(self.division)
        else:
            return str(args[0] / args[1]) 

    def equal(self, *args):
        if self.newest_operation != None: self.newest_operation(None)

    def insert_anything(self, text):
        """
        Metódo responsável por inserir os números nas posições corretas

        text: texto a ser inserido
        """

        if self.local_input.text.find("e") != -1:
            virg = self.local_input.text.find(",")
            self.local_input.text = self.local_input.text[:virg] + text + self.local_input.text[virg:]
        else:
            self.local_input.text += text


class MitC(App):
    def build(self):
        self.icon = "images/icon.png"
        return Main_layout()

if __name__ == "__main__":
    MitC().run()