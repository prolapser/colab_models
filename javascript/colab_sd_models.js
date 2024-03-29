document.addEventListener('DOMContentLoaded', () => {
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes) {
        mutation.addedNodes.forEach((node) => {
          if (node.id === 'tab_models_list') {
            // запуск кода после загрузки элементов
            Array.from(document.querySelectorAll('#tabs > div.tab-nav > button')).find(button => button.textContent.includes('модели')).click();
            // переопределение параметров колонок на основе числа моделей в категории
            const models_checkbox_grids = document.querySelectorAll("#tab_models_list fieldset > div[data-testid='checkbox-group']");
            models_checkbox_grids.forEach(models_checkbox_grid => {
              const model_label = models_checkbox_grid.querySelectorAll('label');
              const numColumns = model_label.length > 9 ? 'repeat(auto-fit, minmax(250px, 1fr))' : '1fr';
              models_checkbox_grid.style.gridTemplateColumns = numColumns;
            });
            // подвсетка категории мужицких моделей (костаыль, потому что градио своим скриптом долбит каждые Nms переопределение классов)
            const intervalId = setInterval(() => {
              const modelsNavButtons = document.querySelectorAll("div#tab_models_list > div.gap > div.tabs > div.tab-nav > button");
              const MaleCat = Array.from(modelsNavButtons).find(button => button.textContent.includes('мужские'));
              if (MaleCat) {
                MaleCat.setAttribute("id", "male_only");
              }
            }, 100);
            // получение инфы по кд о свободном пространтсве из скрытого уродского текстбокса в красивый элементик в шапочке
            const freespacetextarea = document.querySelector("#free_space_area > label > textarea");
            const frespace_out = document.querySelector("#frespace_out");
            let prevValue = freespacetextarea.value;
            setInterval(function () {
              const currentValue = freespacetextarea.value;
              if (currentValue !== prevValue) {
                frespace_out.innerHTML = `${currentValue}`;
                prevValue = currentValue;
              }
            }, 100);
            // скликивание реальной но скрытой уродской кнопки с обработчиком проверки свободного места при нажатии на фейковую но красивую кнопочку
            const freespace_getButton = document.querySelector("#freespace_get");
            const free_spaceOrigButton = document.querySelector("#free_space_button");
            freespace_getButton.addEventListener("click", function () {
              free_spaceOrigButton.click();
            });
            // копирование реальных элементов из вкладок с моделями в результатах поиска
            const SearchBlock = document.querySelector('#clear_search_models_results').closest('label').closest('div').closest('div').closest('div');
            const ModelDLHeaderBlock = document.querySelector('.models_dl_header').closest('div').parentNode.closest('div').closest('div');
            const ModelDLHeaderContainer = document.querySelector('.models_dl_header').closest('div').parentNode;
            ModelDLHeaderBlock.appendChild(SearchBlock);
            // небольшой css-фикс
            ModelDLHeaderContainer.style.cssText = `display: flex; flex-direction: row; align-items: center; justify-content: flex-start; flex-wrap: wrap;`;
            document.querySelector('.models_dl_header').parentNode.style.marginRight = "50px";
            // фильтрация моделей при вводе
            const searchInput = document.querySelector('input[type="text"]');
            const findedModels = document.querySelector('#finded_models');
            const tabModelsList = document.querySelector('#tab_models_list');
            const labels = tabModelsList.querySelectorAll('label');
            const clearSearchResultsButton = document.querySelector("#clear_search_models_results");
            searchInput.addEventListener('input', (event) => {
              const searchTerm = event.target.value.toLowerCase();
              findedModels.innerHTML = '';
              if (searchTerm !== '') {
                labels.forEach((label) => {
                  const labelText = label.textContent.toLowerCase();
                  if (labelText.includes(searchTerm)) {
                    const clone = label.cloneNode(true);
                    findedModels.appendChild(clone);
                    const originalCheckbox = label.querySelector('input[type="checkbox"]');
                    const clonedCheckbox = clone.querySelector('input[type="checkbox"]');
                    clonedCheckbox.addEventListener('change', () => {
                      originalCheckbox.click();
                    });
                  }
                });
              }
            });
            // обработчик на кнопочку очистки результатов
            clearSearchResultsButton.addEventListener('click', () => {
              findedModels.innerHTML = '';
              searchInput.value = '';
            });
            // автоматическое скликивание скрытых кнопок для подгрузки установленных моделей и свободного места после загрузки дополнения через 1 сек
            setTimeout(() => document.querySelector("#files_button").click(), 1000);
            setTimeout(() => document.querySelector("#free_space_button").click(), 1000);
            // файловый менеджер на тексбоксах
            setTimeout(() => {
              const filesArea = document.querySelector("#files_area > label > textarea");
              const filesCheckbox = document.querySelector("#files_checkbox");
              const deleteArea = document.querySelector("#delete_area > label > textarea");
              // обновление списка чекбоксов с файлами при изменении списка путей в текстбоксе
              function addCheckboxEventListeners() {
                const delete_checkboxes = document.querySelectorAll("#files_checkbox > label > input[type=checkbox]");
                delete_checkboxes.forEach(checkbox => {
                  checkbox.addEventListener("change", event => {
                    // отмеченные на удаление делаем красными и зачеркнутыми
                    const delete_span = event.target.parentElement.querySelector("span");
                    if (event.target.checked) {
                      delete_span.style.textDecoration = "line-through";
                      delete_span.style.color = "#ed5252";
                    } else {
                      delete_span.style.textDecoration = "none";
                      delete_span.style.color = "";
                    }
                  });
                });
              }
              // функция для обновления чекбоксов с файлами почти в реальном времени
              function updateCheckboxes() {
                while (filesCheckbox.firstChild) {
                  filesCheckbox.removeChild(filesCheckbox.firstChild);
                }
                const fileNames = filesArea.value.split("\n").map(path => path.split("/").pop());
                if (fileNames.length === 0 || (fileNames.length === 1 && fileNames[0] === "")) {
                  const message = document.createElement("p");
                  message.textContent = "ничего не найдено";
                  filesCheckbox.appendChild(message);
                } else {
                  fileNames.forEach(fileName => {
                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.id = fileName;
                    checkbox.addEventListener("change", event => {
                      if (event.target.checked) {
                        deleteArea.value += (deleteArea.value ? "\n" : "") + fileName;
                      } else {
                        const lines = deleteArea.value.split("\n");
                        const index = lines.indexOf(fileName);
                        if (index !== -1) {
                          lines.splice(index, 1);
                          deleteArea.value = lines.join("\n");
                        }
                      }
                      deleteArea.dispatchEvent(new Event('input')); // имитация ввода, это самая важная часть кода
                    });
                    const label = document.createElement("label");
                    label.htmlFor = fileName;
                    label.className = "filecheckbox";
                    const span = document.createElement("span");
                    span.textContent = fileName;
                    label.appendChild(checkbox);
                    label.appendChild(span);
                    filesCheckbox.appendChild(label);
                  });
                }
                deleteArea.value = deleteArea.value.trim();
                deleteArea.dispatchEvent(new Event('input')); // имитация ввода, без этого не работает
                addCheckboxEventListeners()
              }
              // наблюдаем за скрытым тексбоксом с путями до моделей и обновлям чекбоксы
              const observer = new MutationObserver(updateCheckboxes);
              observer.observe(filesArea, { characterData: true, subtree: true });
              updateCheckboxes();
              // скликивание реальной но скрытой уродской кнопки с обработчиком обновления списка файлов при нажатии на фейковую но красивую кнопочку
              const RefreshFilesButton = document.querySelector("#refresh_files_button");
              RefreshFilesButton.addEventListener("click", () => {
                document.querySelector("#files_button").click();
                // задержки по 3 секунды необходимы, чтобы колаб одуплился
                setTimeout(function () { updateCheckboxes(); }, 3000);
              });
              // при клике на фейковую кнопочку удаления - произойдет и обновление списка файлов с задержкой 3 сек
              document.querySelector("#delete_button").addEventListener("click", function () {
                setTimeout(function () {
                  document.querySelector("#files_button").click();
                  // задержки по 3 секунды необходимы, чтобы колаб одуплился
                  setTimeout(function () { updateCheckboxes(); }, 3000);
                }, 3000);
              });
              // скликивание реальной но скрытой уродской кнопки с обработчиком удаления моделей при нажатии на фейковую но красивую кнопочку
              const OrigDelButton = document.querySelector("#delete_button");
              const CustomDelButton = document.querySelector("#delete_files_button");
              CustomDelButton.addEventListener("click", () => {
                OrigDelButton.click();
              });
              // проверка выхлопа из функции загрузки в скрытом текстбоксе
              setInterval(function () {
                var DLresultText = document.querySelector("#downloads_result_text > span.finish_dl_func");
                DLresultText.textContent = document.querySelector("#dlresultbox > label > textarea").value;
                // функция скрытия прогрессбара
                function checkDLresult(element, text) {
                  if (element.textContent.includes(text)) {
                    document.querySelector("div.downloads_result_container > div.models_porgress_loader").style.removeProperty("display");
                    document.querySelector("#downloads_start_text").style.removeProperty("display");
                    document.querySelector("#downloads_result_text > span.dl_progress_info").textContent = "чтобы новые файлы появились в выпадающем списке моделей, нужно обновить их список по соответсвующей кнопке";
                  }
                }
                // просто скрываем прогрессбар если в выхлопе есть фраза о завершении или предупреждение
                checkDLresult(DLresultText, "заверш");
                checkDLresult(DLresultText, "слишком");
                checkDLresult(DLresultText, "ОШИБКА");
                // раскрашиваем текст сообщения о результате выполнения, если что-то пошло не так
                if (DLresultText) {
                  if (DLresultText.textContent.includes("слишком")) {
                    DLresultText.style.setProperty("color", "#ff4f8b", "important");
                  } else if (DLresultText.textContent.includes("ОШИБКА")) {
                    DLresultText.style.setProperty("color", "#de2f2f", "important");
                  } else if (DLresultText.textContent.includes("заверш")) {
                    DLresultText.style.setProperty("color", "#99fb99", "important");
                  }
                }
              }, 200);
              // действия по клику на фейковую но видимую кнопку для скачивания
              document.querySelector("#general_download_button").addEventListener("click", function () {
                // очистка текстбокса от выхлопа предыдущего выполнения
                var resultTextareaDL = document.querySelector("#dlresultbox > label > textarea");
                resultTextareaDL.value = "";
                var resultClearOut = new Event("input", { bubbles: true }); // без этого не будет работать обноволение .value
                resultTextareaDL.dispatchEvent(resultClearOut);
                // делаем прогрессбар и место для результирующего текста видимыми
                const DLprogressBar = document.querySelector("div.downloads_result_container > div.models_porgress_loader");
                DLprogressBar.style.setProperty("display", "block", "important");
                const DLresultText = document.querySelector("#downloads_result_text");
                DLresultText.style.setProperty("display", "block", "important");
                document.querySelector("#downloads_start_text").style.setProperty("display", "block", "important");
                // скликивание реальных но скрытых кнопок с обработчиками загрузки файлов по чекбоксам и кастомных ссылок при нажатии на фейковую но кнопочку
                // формирование списка из кастомных ссылок
                document.querySelector("#ownlinks_download_button").click();
                setTimeout(function () {
                  // через 3 сек. добавим его к списку ссылок из чекбоксов и отправим на загрузку вместе
                  document.querySelector("#checkboxes_download_button").click();
                }, 3000); // задержка, чтобы колаб успел одуплиться
              });
              // если кнопка загрузки уже нажата, запрещаем кликать еще раз пока функция загрузки не выплюнет ответ
              var GendownloadButton = document.querySelector("#general_download_button");
              var DLprogressBar = document.querySelector("div.downloads_result_container > div.models_porgress_loader");
              if (GendownloadButton && DLprogressBar) {
                var DLobserver = new MutationObserver(function (mutations) {
                  mutations.forEach(function (mutation) {
                    if (mutation.type === "attributes" && mutation.attributeName === "style") { // отслеживание видимости прогрессбара
                      if (DLprogressBar.style.display === "block") {
                        GendownloadButton.setAttribute("disabled", "disabled");
                      } else {
                        setTimeout(function () {
                          GendownloadButton.removeAttribute("disabled");
                        }, 3000); // не сразу даем кликнуть снова, а после ожидания 3 секунды, чтобы не закликали
                      }
                    }
                  });
                });
                DLobserver.observe(DLprogressBar, { attributes: true });
              }
            }, 9000); // запуск скриптов через 9 секунд после загрузки вебуи, чтобы успели отработать скрипты других дополнений и градио
          }
        });
      }
    });
  });
  observer.observe(document.body, { childList: true, subtree: true });
});
