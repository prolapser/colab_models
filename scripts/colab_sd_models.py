# -*- coding: utf-8 -*-
import os, re, requests, subprocess, shutil
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import gradio as gr
from bs4 import BeautifulSoup
from modules import scripts, script_callbacks

urlprefix = "https://huggingface.co/2ch/models/resolve/main/"
models_json_data = requests.get(urlprefix+"colab_models.json").json()
wget = "wget -nv -t 10 --show-progress --progress=bar:force -q --content-disposition "
sdroot = "/".join(os.path.realpath(__file__).split("extensions")[0].split("/")[:-1])
models_folder_path = os.path.join(sdroot,"models/Stable-diffusion")
loras_folder_path = os.path.join(sdroot,"models/Lora")
embeddings_folder_path = os.path.join(sdroot,"embeddings")
ct = "token=542c1d6077168822e1b49e30e3437a5d"

def on_ui_tabs():
    with gr.Blocks() as models_list:
        # шапка вкладки с поиском и свободным местом на диске
        gr.HTML("""<div class="models_top_container"><div class="models_top_header_text"><h1 class="models_dl_header">выбор и скачивание моделей</h1><p>учитывай весьма ограниченное пространство на диске в колабе!</p></div><div class="freespaceinfo"><div id="frespace_output"><span>свободно в колабе: <span id="frespace_out">нажми на кнопочку</span></div><div id="freespace_get"></div></div></div>""")
        search_and_results = gr.HTML("""<label id="models_search_field"><input type="text" id="models_search_input" class="svelte-1pie7s6" placeholder="начни вводить для поиска"/><span id="clear_search_models_results"></span></label><div id="finded_models"></div>""")
        # вкладки с категориями
        buttons = []
        checkbox_groups = []
        checkboxes = []
        for category in models_json_data['categories']:
            categories = ["models_A", "models_B", "models_C", "models_D", "models_E", "models_F", "models_G", "models_H", "models_I", "models_J", "models_K", "models_L", "models_M", "models_N", "models_O", "models_P", "models_Q"]
            tab_names = ["аниме", "лайнарт", "женские", "игры и кино", "техника и космос", "крипота", "макро", "мемные", "мужские", "мультфильмы", "пиксельарт", "трехмерная графика", "универсальные", "фотореализм", "фурри", "футанари", "художественные"]
            category_map = dict(zip(categories, tab_names))
            tab_name = category_map.get(category)
            with gr.Tab(tab_name):
                checkbox_group = gr.CheckboxGroup(sorted(models_json_data['categories'][category], key=lambda x: x.lower()), label="")
                checkboxes.append(checkbox_group)
                checkbox_groups.append(checkbox_group)
        # ссылки для реквеста добавления моделей
        gr.HTML("""<div class="request_new_models">не нашел нужную модель? запрос на добавление можно отправить в <a href="https://t.me/colabSDbot" target="_blank">бота</a> или <a href="https://t.me/stabdiff" target="_blank">группу</a>.</div>""")
        # функция для формирования списка своих ссылок
        def get_own_links(ownmodels, ownloras, ownembeddings):
            urls = []
            for text, dlpath in zip([ownmodels, ownloras, ownembeddings], [models_folder_path, loras_folder_path, embeddings_folder_path]):
                lines = text.split("\n")
                for line in lines:
                    if line.strip():
                        # url = wget+line+" -P "+dlpath
                        link = line.strip() + (f'?{ct}' if '?' not in line else f'&{ct}') if 'civitai' in line else line.strip()
                        url = f'{wget}"{link}" -P {dlpath}'
                        urls.append(url)
            own_urls = os.path.join(sdroot,"urls.txt")
            with open(own_urls, "w") as f:
                for url in urls:
                    f.write(url + "\n")
            print("список загрузки сформирован...")
        # текстбоксы для указания своих ссылок
        gr.HTML("""<div class="ownfiles_header"><h2>здесь можно указать прямые ссылки на загрузку моделей, лор и внедрений</h2></div>""")
        with gr.Row():
            plhd = """вставляй каждую ссылку с новой строки!\nпримеры ссылок:\nhttps://models.tensorplay.ai/104249\nhttps://civitai.com/api/download/models/110660\nhttps://huggingface.co/2ch/gay/resolve/main/lora/BettercocksFlaccid.safetensors"""
            ownmodels = gr.Textbox(label="модели", placeholder=plhd, info="прямые ссылки на Checkpoints", lines=5, elem_id="ownmodels")
            ownloras = gr.Textbox(label="лоры", placeholder=plhd, info="прямые ссылки на LoRas", lines=5, elem_id="ownloras")
            ownembeddings = gr.Textbox(label="внедрения", placeholder=plhd, info="прямые ссылки на Textual Inversions", lines=5, elem_id="ownembeddings")
        # кнопка при нажатии на которую происходит сначала клик на кнопку формирования списка своих ссылок, а потом на кнопку основной функции загрузки
        download_button = gr.Button("скачать выбранные модели", elem_id="general_download_button")
        # кнопка для формирования списка своих ссылок
        button = gr.Button("скачать по ссылкам", elem_id="ownlinks_download_button")
        button.click(get_own_links, inputs=[ownmodels, ownloras, ownembeddings])
        # кнопка для отправки на загрузку
        download_button = gr.Button("скачать отмеченные модели", elem_id="checkboxes_download_button")
        # функция определения точки монтирования и свободного места на диске
        def find_mount_point():
            #__file__ = "."
            path = os.path.realpath(__file__)
            path = os.path.abspath(path)
            while not os.path.ismount(path):
                path = os.path.dirname(path)
            return path
        def free_space():
            total, used, free = shutil.disk_usage(find_mount_point())
            power = 2**10
            n = 0
            power_labels = {0 : '', 1: 'Кило', 2: 'Мега', 3: 'Гига', 4: 'Тера'}
            while free > power:
                free /= power
                n += 1
            return f"{free:.2f} {power_labels[n]}байт"
        # функция вычисления общего размера загружаемых файлов в байтах
        def get_file_size(url):
            url = re.search(r'https?://\S+', url).group()
            def contleght(url): return int(requests.get(url, stream=True).headers.get('Content-Length', 0))
            if "huggingface" in url:
                try:
                  try:
                      file_size = int(next((pre.text.split('size ')[1].split('\n')[0] for pre in BeautifulSoup(requests.get(url.replace('resolve', 'blame')).text, 'html.parser').find_all('pre') if 'size' in pre.text)))
                  except:
                      file_size_text = BeautifulSoup(requests.get(url.replace('resolve', 'blob')).text, 'html.parser').find('strong', string='Size of remote file:').next_sibling.strip()
                      file_size = int(float(file_size_text.split()[0]) * {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}[file_size_text.split()[1]])
                except:
                    file_size = contleght(url)
                if file_size < 1048576: file_size = contleght(url)
            elif "civitai" in url:
                try:
                    file_size = int(requests.get("https://civitai.com/api/v1/model-versions/"+url.split('/')[-1]+civitai_token).json()["files"][0]["sizeKB"] * 1024)
                except:
                    file_size = contleght(url)
                if file_size < 1048576: file_size = contleght(url)
            else:
                file_size = contleght(url)
            return file_size
        # основная функция для загрузки отмеченных чекбоксов
        def start_download(*checkbox_groups):
            try:
                urls = []
                for checkbox_group in checkbox_groups:
                    selected_choices = checkbox_group
                    for choice in selected_choices:
                        if choice in models_json_data["models"]:
                            file_names = models_json_data["models"][choice].split(',')
                            for file_name in file_names:
                                url = wget+urlprefix+file_name.strip()+" -P "+models_folder_path
                                urls.append(url)
                own_urls = os.path.join(sdroot,"urls.txt")
                with open(own_urls, "r") as f:
                    own_links = f.read().splitlines()
                urls.extend(own_links)
                os.remove(own_urls)
            except Exception as e:
                print(f"ОШИБКА: {e}")
                return f"ОШИБКА: {e}"
            try:
                def bytes_convert(size_bytes):
                    if size_bytes >= 1073741824: return f"{round(size_bytes / 1073741824, 2)} Гб"
                    else: return f"{round(size_bytes / 1048576, 2)} Мб"
                def downloader(url):
                    process = subprocess.Popen(url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    while True:
                        output = process.stdout.readline().decode('utf-8')
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            yield output.strip()
                    return process.poll()
                total_file_size = 0
                with ThreadPoolExecutor(max_workers=len(urls)) as executor:
                    futures = [executor.submit(get_file_size, url) for url in urls]
                    for future in as_completed(futures):
                        total_file_size += future.result()
                total, used, free = shutil.disk_usage(find_mount_point())
                if total_file_size <= (free - 1073741824):
                    print(f"загрузка {bytes_convert(total_file_size)} уже началась, жди!")
                    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
                        futures = [executor.submit(downloader, url) for url in urls]
                        for future in as_completed(futures):
                            for line in future.result():
                                print(line)
                    if os.path.exists(os.path.join(models_folder_path, "nullModel.ckpt")):
                        try:
                            os.remove(os.path.join(models_folder_path, "nullModel.ckpt"))
                        except:
                            pass
                    return "функция загрузки завершила работу!"
                else:
                    print(f"слишком много файлов! ты пытаешься скачать {bytes_convert(total_file_size)}, имея свободных только {bytes_convert(free)} (и как минимум 1 Гб должен оставаться не занятым на диске!).")
                    return f"слишком много файлов! ты пытаешься скачать {bytes_convert(total_file_size)}, имея свободных только {bytes_convert(free)} (и как минимум 1 Гб должен оставаться не занятым на диске!)."
            except Exception as e:
                print(f"ОШИБКА: {e}")
                return f"ОШИБКА: {e}"
        # скрытый текстбокс для вывода информации о результате
        dlresultbox = gr.Textbox(label="", elem_id="dlresultbox")
        download_button.click(start_download, inputs=checkbox_groups, outputs=dlresultbox)
        # анимация процесса выполнения функции загрузки
        gr.HTML("""<div class="downloads_result_container"><div class="models_porgress_loader"></div><div id="downloads_start_text">задача по загрузке запущена, подробности в выводе ячейки в колабе...</div><div id="downloads_result_text"><span class="finish_dl_func"></span><span class="dl_progress_info"></span></div></div>""")
        # скрытые элементы для взаимодействия с функцией определения места на диске
        spacetextbox = gr.Textbox(label="", elem_id="free_space_area")
        space_button = gr.Button("проверить свободное место", elem_id="free_space_button")
        space_button.click(fn=free_space, outputs=spacetextbox)
        # HTML-разметка для формирования чекбоксов для удаления файлов моделей
        gr.HTML("""<hr class="divider"/><div id="filemanager"><h2 class="current_models_files">файлы моделей которые можно удалить для освобождения места:</h2><div id="files_checkbox"></div><div class="filebuttons"><div id="delete_files_button"></div><div id="refresh_files_button"></div></div></div>""")
        # функция получения путей до установленных файлов моделей
        def get_models_paths():
            file_paths = []
            for root, dirs, files in os.walk(models_folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
            return '\n'.join(file_paths)
        # скрытые текстбокс и кнопка для получения списка файлов из папки моделей
        filestextbox = gr.Textbox(label="", elem_id="files_area")
        files_button = gr.Button("установленные модели", elem_id="files_button")
        files_button.click(fn=get_models_paths, outputs=filestextbox)
        # функция удаления списка отмеченных файлов
        def del_models(inputs):
            files_to_delete = inputs.split("\n")
            for file in files_to_delete:
                if file and file != "None":
                    try:
                        os.remove(os.path.join(models_folder_path, file))
                        print(f"успешно удалена модель: {file}")
                    except OSError as e:
                        print(f"ОШИБКА: {e.filename} - {e.strerror}.")
                else:
                    print("удалять нечего, или ничего не выбрано для удаления")
        # скрытые текстбокс и кнопка для формирования списка файлов на удаление
        deletetextbox = gr.Textbox(label="", elem_id="delete_area")
        delete_button = gr.Button("удалить", elem_id="delete_button")
        delete_button.click(fn=del_models, inputs=deletetextbox, outputs=deletetextbox)
        with gr.Accordion("описания моделей (не обновляется)", open=False):
            gr.HTML(requests.get("https://raw.githubusercontent.com/PR0LAPSE/PR0LAPSE.github.io/main/models.html").text)
    # возврат всех элементов
    return (models_list, "модели", "models_list"),
# вывод в вебуи
script_callbacks.on_ui_tabs(on_ui_tabs)
