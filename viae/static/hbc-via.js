//
// Initialization routine
//

function _hbc_via_init() {
    console.log(VIA_NAME);
    show_message(`${VIA_NAME}(${VIA_SHORT_NAME}) version ${VIA_VERSION}. Ready !`, 2*VIA_THEME_MESSAGE_TIMEOUT_MS);
    document.getElementById('img_fn_list').style.display = 'block';
    document.getElementById('leftsidebar').style.display = 'table-cell';

    // initialize default project
    project_init_default_project();

    // initialize image grid
    image_grid_init();

    show_single_image_view();
    init_leftsidebar_accordion();
    hbc_hide_attributes_editor();
    attribute_update_panel_set_active_button();
    annotation_editor_set_active_button();
    init_message_panel();

    // submodules: fetch images from in_progress S3 bucket, preload label dropdown, render annotations
    if (typeof _hbc_via_load_submodules === 'function') {
      console.log('Loading VIA submodule');
      _hbc_via_load_submodules();
    }
}


function hbc_hide_attributes_editor() {
  leftsidebar_show();
  document.getElementById('attributes_editor_panel').classList.toggle('hide');
  document.getElementById('attributes_editor_panel_title').classList.toggle('hide');
}


function _hbc_via_load_submodules() {
     _via_current_shape = VIA_REGION_SHAPE.POLYGON;  // preload polygon shape as default
    _hbc_via_basic_demo_load_img();
    _hbc_via_basic_demo_define_attributes();
    //_via_basic_demo_define_annotations();
    //toggle_attributes_editor();
    //update_attributes_update_panel();
    toggle_annotation_editor();
}


// GET in_progress data
function _hbc_via_basic_demo_load_img() {
    const url = `/images/in_progress`;
    fetch(url)
    .then((resp) => resp.json())
    .then(function(image_data) {
        var filenames = []
        for (var fname in image_data) {
          var f = image_data[fname].filename;
          filenames.push(f);
        }
        // add files
        let n = filenames.length;
        filenames.forEach( (filename) => {
          project_file_add_base64(filename, filename);
        });
        _via_show_img(0);
        hbc_update_img_fn_list(filenames);
        hbc_import_annotations_from_json(image_data);
        })
}


// Load predefined label classes from static/attributes.js for poulating dropdown
function _hbc_via_basic_demo_define_attributes() {
  var attributes_json = JSON.stringify(label_attributes);
  project_import_attributes_from_json(attributes_json);
}


// load in_progress annotation data and render to user
function hbc_import_annotations_from_json(data) {
  console.log('importing annotations:')
  console.log(data);
  return new Promise( function(ok_callback, err_callback) {
    if (data === '' || typeof(data) === 'undefined') {
      return;
    }

    let region_import_count = 0;
    let file_added_count    = 0;
    let malformed_entries_count    = 0;
    for (var img_id in data) {
      var filename = data[img_id].filename;
      var size     = data[img_id].size;
      var attr     = data[img_id].file_attributes;
      var regions  = data[img_id].regions;
      var img_id1  = _via_get_image_id(filename, -1);
      if ( ! _via_img_metadata.hasOwnProperty(img_id1) ) {
        img_id1 = project_add_new_file(filename, size);
        if ( _via_settings.core.default_filepath === '' ) {
          _via_img_src[img_id1] = filename;
        } else {
          _via_file_resolve_file_to_default_filepath(img_id1);
        }
        console.log("Adding new file " + img_id1);
        file_added_count += 1;
      }

      // copy file attributes
      var key;
      for ( key in attr ) {
        if ( key === '' ) {
          continue;
        }

        _via_img_metadata[img_id1].file_attributes[key] = data[img_id].file_attributes[key];

        // add this file attribute to _via_attributes
        if ( ! _via_attributes['file'].hasOwnProperty(key) ) {
          _via_attributes['file'][key] = { 'type':'text' };
        }
      }

      // copy regions
      var key, i;
      for ( i in regions ) {
        var region_i = new file_region();
        region_i.annotation_id = regions[i].annotation_id;
        for ( key in regions[i].shape_attributes ) {
          region_i.shape_attributes[key] = regions[i].shape_attributes[key];
        }
        for ( var key in regions[i].region_attributes ) {
          if ( key === '' ) {
            continue;
          }

          region_i.region_attributes[key] = regions[i].region_attributes[key];

          // add this region attribute to _via_attributes
          if ( ! _via_attributes['region'].hasOwnProperty(key) ) {
            _via_attributes['region'][key] = { 'type':'text' };
          }
        }

        // add regions only if they are present
        if ( Object.keys(region_i.shape_attributes).length > 0 ||
             Object.keys(region_i.region_attributes).length > 0 ) {
          _via_img_metadata[img_id1].regions.push(region_i);
          region_import_count += 1;
        }
      }
    }
    show_message('Import Summary : [' + file_added_count + '] new files, ' +
                 '[' + region_import_count + '] regions, ' +
                 '[' + malformed_entries_count + '] malformed entries.');

    if ( file_added_count ) {
      update_img_fn_list();
    }

    if ( _via_current_image_loaded ) {
      if ( region_import_count ) {
        update_attributes_update_panel();
        update_annotation_editor();
        _via_load_canvas_regions(); // image to canvas space transform
        _via_redraw_reg_canvas();
        _via_reg_canvas.focus();
      }
    } else {
      if ( file_added_count ) {
        _via_show_img(0);
      }
    }

    ok_callback([file_added_count, region_import_count, malformed_entries_count]);
  });
}


function hbc_update_img_fn_list(filenames) {
    const regex = document.getElementById('img_fn_list_regex').value;
    const p = document.getElementById('filelist_preset_filters_list');
    if ( regex === '' || regex === null ) {
      if ( p.selectedIndex === 0 ) {
        // show all files
        _via_img_fn_list_html = [];
        _via_img_fn_list_img_index_list = [];
        _via_img_fn_list_html.push('<ul>');
        for ( var i=0; i < filenames.length; ++i ) {
          _via_img_fn_list_html.push( hbc_img_fn_list_ith_entry_html(i, filenames) );
          _via_img_fn_list_img_index_list.push(i);
        }
        _via_img_fn_list_html.push('</ul>');
        img_fn_list.innerHTML = _via_img_fn_list_html.join('');
        img_fn_list_scroll_to_current_file();
      } else {
        // filter according to preset filters
        img_fn_list_onpresetfilter_select();
      }
    } else {
      img_fn_list_generate_html(regex);
      img_fn_list.innerHTML = _via_img_fn_list_html.join('');
      img_fn_list_scroll_to_current_file();
    }
  }

function hbc_img_fn_list_ith_entry_html(i, filenames) {
  let htmli = '';
  let filename = filenames[i];
  if ( is_url(filename) ) {
    filename = filename.substr(0,4) + '...' + get_filename_from_url(filename);
  }

  htmli += '<li id="fl' + i + '"';
  if ( _via_display_area_content_name === VIA_DISPLAY_AREA_CONTENT_NAME.IMAGE_GRID ) {
    if ( _via_image_grid_page_img_index_list.includes(i) ) {
      // highlight images being shown in image grid
      htmli += ' class="sel"';
    }

  } else {
    if ( i === _via_image_index ) {
      // highlight the current entry

      htmli += ' class="sel"';
    }
  }
  htmli += ` onclick="jump_to_image( ${(i)})" title=" ${filename} ">[ ${(i+1)}] ${filename} </li>`;

  return htmli;
}

//
// End of Initialization routine
//


function hbc_project_file_add_url_with_input() {
  const config = {
    'title':'Add File using URL'
  };
  const input = {
    'url': {
      type:'text',
      name:'add one URL',
      placeholder:'http://www.example.com/image1.jpg',
      disabled:false,
      size:50
    },
    'url_list': {
      type:'textarea',
      name:'or, add multiple URL (one url per line)',
      placeholder:'http://www.example.com/image1.jpg\nhttp://www.example.com/image2.jpg\nhttp://www.example.com/image3.png',
      disabled:false,
      rows:5,
      cols:80
    }        
  };

  invoke_with_user_inputs(hbc_project_file_add_url_input_done, input, config);
}

function hbc_project_file_add_url_input_done(input) {
  if ( input.url.value !== '' ) {
    var url = input.url.value.trim();
    hbc_post_url_to_server(url);
  } else {
    if ( input.url_list.value !== '' ) {
      var url_list_str = input.url_list.value;
      hbc_post_url_to_server(url_list_str);
    }
  }
}

//
// post url to server (user adds new file via url path)
//

function hbc_post_url_to_server(url_str) { // NB: url_str is either 'url1' or 'url1\nurl2\nurl3\n...'
  const url = new URL(`${window.location}images/in_progress`);
  params = {url: true};
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  url_enc = encodeURIComponent(url_str);
  fetch(url, {
    method: 'POST',
    body: (JSON.stringify(url_enc))
  })
  .then(response => response.json())
  .catch(error => console.error('Error:', error))
  .then(function(files_with_coco) {
    for ( let i = 0; i < files_with_coco.length; ++i ) {
      var img_id    = project_file_add_url(files_with_coco[i].image_url);
      var img_index = _via_image_id_list.indexOf(img_id);
      show_message('Added file at url [' + url + ']');
      update_img_fn_list();
      _via_show_img(img_index);
      user_input_default_cancel_handler();
    }
  });
}


// Submit new image files to server (when user clicks 'add files')
function hbc_sel_local_images() {
  // source: https://developer.mozilla.org/en-US/docs/Using_files_from_web_applications
  if (invisible_file_input) {
    invisible_file_input.setAttribute('multiple', 'multiple')
    invisible_file_input.accept   = '.jpg,.jpeg,.png,.bmp';
    invisible_file_input.onchange = hbc_project_file_add_local;
    invisible_file_input.click();
  }
}


function hbc_project_file_add_local(event) {
  var user_selected_images = event.target.files;
  hbc_post_new_file_to_server(user_selected_images);
}


function hbc_post_new_file_to_server(user_selected_images) {
  const url = new URL(`${window.location}images/in_progress`);
  params = {url: false};
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))
  const formData = new FormData();
  for ( let i = 0; i < user_selected_images.length; ++i ) {
    formData.append(`file_${i}`, user_selected_images[i]);
  }
  fetch(url, {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .catch(error => console.error('Error:', error))
  .then(function(image_data) {
    hbc_update_img_name_in_panel(image_data, user_selected_images);
  })
}

function hbc_update_img_name_in_panel(image_data_w_coco, user_selected_images) {
  var original_image_count = _via_img_count;
  var new_img_index_list = [];
  var discarded_file_count = 0;
  for ( var i = 0; i < user_selected_images.length; ++i ) {
    var filetype = user_selected_images[i].type.substr(0, 5);
    if ( filetype === 'image' ) {
      var filename = user_selected_images[i].name;
      var size     = user_selected_images[i].size;
      var img_id1  = _via_get_image_id(filename, size);
      var img_id2  = _via_get_image_id(filename, -1);
      var img_id   = img_id1;

      if ( _via_img_metadata.hasOwnProperty(img_id1) || _via_img_metadata.hasOwnProperty(img_id2) ) {
        if ( _via_img_metadata.hasOwnProperty(img_id2) ) {
          img_id = img_id2;
        }
        _via_img_fileref[img_id] = user_selected_images[i];
        if ( _via_img_metadata[img_id].size === -1 ) {
          _via_img_metadata[img_id].size = size;
        }
      } else {
        filename_s3 = image_data_w_coco[i].image_url
        img_id = project_add_new_file(filename_s3, size);
        _via_img_fileref[img_id] = user_selected_images[i];
        set_file_annotations_to_default_value(img_id);
      }
      new_img_index_list.push( _via_image_id_list.indexOf(img_id) );
    } else {
      discarded_file_count += 1;
    }
  }

  if ( _via_img_metadata ) {
    var status_msg = `Loaded ${new_img_index_list.length} images.`; //
    if ( discarded_file_count ) {
      status_msg += ' ( Discarded ' + discarded_file_count + ' non-image files! )';
    }
    show_message(status_msg);

    if ( new_img_index_list.length ) {
      // show first of newly added image
      _via_show_img( new_img_index_list[0] );
    } else {
      // show original image
      _via_show_img ( _via_image_index );
    }
    update_img_fn_list();
  } else {
    show_message("Please upload some image files!");
  }
}


//
// Submit finished labeling data to server
//

// ref in via.js: download_all_region_data
function hbc_submit_all_region_data(type) {
  // Javascript strings (DOMString) is automatically converted to utf-8
  // see: https://developer.mozilla.org/en-US/docs/Web/API/Blob/Blob
  const all_region_data = pack_via_metadata(type);  // this is [string] of length 1, containing exported labeling data for all images in project panel
  const all_region_data_obj = JSON.parse(all_region_data[0]);
  const curr_img_data = Object.values(all_region_data_obj)[_via_image_index];
  const img_url1 = curr_img_data.filename;
  const file_name = img_url1.replace(/.*\/([^\/]+)$/,'$1');  // remove prefix 'https://s3.amazonaws.com/cerebro-image-annotations/in-progress/'
  const s3_image_id = file_name.replace(/^([0-9]{5}).*/, '$1');   // remove everything except image id
  hbc_project_file_submit_with_confirm(s3_image_id, curr_img_data);
}


function hbc_project_file_submit_with_confirm(s3_image_id, curr_img_data) {
  var img_id = _via_image_id_list[_via_image_index];
  var filename = _via_img_metadata[img_id].filename;
  var region_count = _via_img_metadata[img_id].regions.length;

  if (region_count === 0) {
    show_message('Please add annotations to file [' + filename + ']. Aborting submit.');
    user_input_cancel_handler();
  } else {
  var config = {'title':'Submit file to S3 and remove from project?' };
  var input = { 'img_index': { type:'text', name:'File Id', value:(_via_image_index+1), disabled:true, size:8 },
                'filename':{ type:'text', name:'Filename', value:filename, disabled:true, size:30},
                'region_count':{ type:'text', name:'Number of regions', disabled:true, value:region_count, size:8}
              };

  hbc_invoke_with_user_inputs(hbc_project_file_submit_confirmed, input, config, s3_image_id, curr_img_data, 'hbc_submit_to_server');
  }
}


// invoke a method after receiving inputs from user
function hbc_invoke_with_user_inputs(ok_handler, input, config, s3_image_id, payload, fn_call_to_server) {
  hbc_setup_user_input_panel(ok_handler, input, config, s3_image_id, payload, fn_call_to_server);
  show_user_input_panel();
}


function hbc_setup_user_input_panel(ok_handler, input, config, s3_image_id, payload, fn_call_to_server) {
  // create html page with OK and CANCEL button
  // when OK is clicked
  //  - setup input with all the user entered values
  //  - invoke handler with input
  // when CANCEL is clicked
  //  - invoke user_input_cancel()
  _via_user_input_ok_handler = ok_handler;
  //_via_user_input_cancel_handler = cancel_handler;
  _via_user_input_data = input;

  var p = document.getElementById('user_input_panel');
  var c = document.createElement('div');
  c.setAttribute('class', 'content');
  var html = [];
  html.push('<p class="title">' + config.title + '</p>');


  html.push('<div class="user_inputs">');

  if (fn_call_to_server == 'hbc_submit_to_server') {
      // radio buttons html
    html.push('<div class="row">');
    html.push('<span class="cell">Dataset type</span>');
    html.push('<span class="cell_radio_btn"><input class="radio_btn" value="train-data" type="radio" id="radio_btn_train" name="ds_radio">' +
              '<label class="label_radio_btn" for="radio_btn_train">Train</label></span>');
    html.push('<span class="cell_radio_btn"><input class="radio_btn" value="test-data" type="radio" id="radio_btn_test" name="ds_radio">' + 
              '<label class="label_radio_btn" for="radio_btn_test">Test</label> </span>');
    html.push('<span class="cell_radio_btn"><input class="radio_btn" value="validate-data" type="radio" id="radio_btn_validate" name="ds_radio" checked>' + 
              '<label class="label_radio_btn" for="radio_btn_validate">Validate</label> </span>');
    html.push('</div>'); // end of row
  }
  
  var key;
  for ( key in _via_user_input_data ) {
    html.push('<div class="row">');
    html.push('<span class="cell">' + _via_user_input_data[key].name + '</span>');
    var disabled_html = '';
    if ( _via_user_input_data[key].disabled ) {
      disabled_html = 'disabled="disabled"';
    }
    var value_html = '';
    if ( _via_user_input_data[key].value ) {
      value_html = 'value="' + _via_user_input_data[key].value + '"';
    }

    switch(_via_user_input_data[key].type) {
    case 'checkbox':
      if ( _via_user_input_data[key].checked ) {
        value_html = 'checked="checked"';
      } else {
        value_html = '';
      }
      html.push('<span class="cell">' +
                '<input class="_via_user_input_variable" ' +
                value_html + ' ' +
                disabled_html + ' ' +
                'type="checkbox" id="' + key + '"></span>');
      break;
    case 'text':
      var size = '50';
      if ( _via_user_input_data[key].size ) {
        size = _via_user_input_data[key].size;
      }
      var placeholder = '';
      if ( _via_user_input_data[key].placeholder ) {
        placeholder = _via_user_input_data[key].placeholder;
      }
      html.push('<span class="cell">' +
                '<input class="_via_user_input_variable" ' +
                value_html + ' ' +
                disabled_html + ' ' +
                'size="' + size + '" ' +
                'placeholder="' + placeholder + '" ' +
                'type="text" id="' + key + '"></span>');

      break;
    case 'textarea':
      var rows = '5';
      var cols = '50'
      if ( _via_user_input_data[key].rows ) {
        rows = _via_user_input_data[key].rows;
      }
      if ( _via_user_input_data[key].cols ) {
        cols = _via_user_input_data[key].cols;
      }
      var placeholder = '';
      if ( _via_user_input_data[key].placeholder ) {
        placeholder = _via_user_input_data[key].placeholder;
      }
      html.push('<span class="cell">' +
                '<textarea class="_via_user_input_variable" ' +
                disabled_html + ' ' +
                'rows="' + rows + '" ' +
                'cols="' + cols + '" ' +
                'placeholder="' + placeholder + '" ' +
                'id="' + key + '">' + value_html + '</textarea></span>');

      break;

    }
    html.push('</div>'); // end of row
  }
  var payload_str = encodeURIComponent(JSON.stringify(payload));
  html.push('</div>'); // end of user_input div
  html.push('<div class="user_confirm">' +
            '<span class="ok">' +
            '<button id="user_input_ok_button" onclick="hbc_user_input_parse_and_invoke_handler(\'' + s3_image_id + '\', \'' + payload_str + '\', ' + fn_call_to_server + ')">&nbsp;OK&nbsp;</button></span>' +
            '<span class="cancel">' +
            '<button id="user_input_cancel_button" onclick="user_input_cancel_handler()">CANCEL</button></span></div>');
  c.innerHTML = html.join('');
  p.innerHTML = '';
  p.appendChild(c);

}


function hbc_user_input_parse_and_invoke_handler(s3_image_id, payload_str, fn_call_to_server) {
  var payload = JSON.parse(decodeURIComponent(payload_str));
  var elist = document.getElementsByClassName('_via_user_input_variable');
  var i;
  for ( i=0; i < elist.length; ++i ) {
    var eid = elist[i].id;
    if ( _via_user_input_data.hasOwnProperty(eid) ) {
      switch(_via_user_input_data[eid].type) {
      case 'checkbox':
        _via_user_input_data[eid].value = elist[i].checked;
        break;
      default:
        _via_user_input_data[eid].value = elist[i].value;
        break;
      }
    }
  }
  if ( typeof(_via_user_input_data.confirm) !== 'undefined' ) {
    if ( _via_user_input_data.confirm.value ) {
      var destination = _via_user_input_ok_handler(_via_user_input_data);
      if (typeof(destination) !== 'undefined') {
        var dest = {destination: destination};
        payload = {...payload, ...dest};
        fn_call_to_server(s3_image_id, payload);
      } else {
        fn_call_to_server(s3_image_id, payload);
      }
    } else {
      if ( _via_user_input_cancel_handler ) {
        _via_user_input_cancel_handler();
      }
    }
  } else {
    var destination = _via_user_input_ok_handler(_via_user_input_data);
    if (typeof(destination) !== 'undefined') {
      var dest = {destination: destination};
      payload = {...payload, ...dest};
      fn_call_to_server(s3_image_id, payload);
    } else {
      fn_call_to_server(s3_image_id, payload);
    }
  }
  user_input_default_cancel_handler();
}


function hbc_project_file_submit_confirmed(input) {
  var img_index = input.img_index.value - 1;
  var s3_img_url = input.filename.value;
  var filename = s3_img_url.replace(/.*\/([^\/]+)$/,'$1');
  var destinations = document.getElementsByName('ds_radio');
  var destination = 'validate';
  for (var i in destinations) {
    if (destinations[i].checked) {
      destination = destinations[i].value;
    }
  }
  project_remove_file(img_index);

  if ( img_index === _via_img_count ) {
    if ( _via_img_count === 0 ) {
      _via_current_image_loaded = false;
      show_home_panel();
    } else {
      _via_show_img(img_index - 1);
    }
  } else {
    _via_show_img(img_index);
  }
  _via_reload_img_fn_list_table = true;
  update_img_fn_list();
  show_message('Submitted file [' + filename + '] to S3 and removed from project.');
  user_input_default_cancel_handler();
  return destination
}


function hbc_submit_to_server(image_id, data) {
  const url = `/images/in_progress/${image_id}`;
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(data),
    headers:{
      'Content-Type': 'application/json'
    }
  }).then(res => res.json())
  .catch(error => console.error('Error:', error))
  .then(function(response) {
    console.log('success:' + response);
    });
}


//
// delete labeling data from s3 in_progress
//

function hbc_project_file_remove_with_confirm() {
  var img_url1 = _via_image_id_list[_via_image_index];
  var img_url_s3 = img_url1.replace(/(.*\.[a-z]+)-?[0-9]+$/, '$1');
  var filename = _via_img_metadata[img_url1].filename;
  var region_count = _via_img_metadata[img_url1].regions.length;

  const s3_file_name = img_url_s3.replace(/.*\/([^\/]+)$/,'$1');  // remove prefix 'https://s3.amazonaws.com/cerebro-image-annotations/in-progress/'
  const s3_image_id = s3_file_name.replace(/^([0-9]{5}).*/, '$1'); // remove everything except id e.g. 00023

  var config = {'title':'Remove File from Project?' };
  var input = { 'img_index': { type:'text', name:'File Id', value:(_via_image_index+1), disabled:true, size:8 },
              'filename':{ type:'text', name:'Filename', value:filename, disabled:true, size:30},
              'region_count':{ type:'text', name:'Number of regions', disabled:true, value:region_count, size:8}
            };

  hbc_invoke_with_user_inputs(hbc_project_file_remove_confirmed, input, config, s3_image_id, img_url_s3, 'hbc_delete_labeling_data_from_s3');
}


function hbc_project_file_remove_confirmed(input) {
  var img_index = input.img_index.value - 1;
  var fname = input.filename.value;
  project_remove_file(img_index);

  if ( img_index === _via_img_count ) {
    if ( _via_img_count === 0 ) {
      _via_current_image_loaded = false;
      show_home_panel();
    } else {
      _via_show_img(img_index - 1);
    }
  } else {
    _via_show_img(img_index);
  }
  _via_reload_img_fn_list_table = true;
  update_img_fn_list();
  show_message('Removed file [' + fname + '] from project.');
  user_input_default_cancel_handler();
}


function hbc_delete_labeling_data_from_s3(s3_image_id, img_url_s3) {
  const url = `images/in_progress/${s3_image_id}`;
  fetch(url, {
    method: 'DELETE',
    body: JSON.stringify(img_url_s3),
    headers:{
      'Content-Type': 'application/json'
    }
  }).then(res => res.json())
  .catch(error => console.error('Error:', error))
  .then(function(response) {
    console.log('success:' + response);
  })
}


//
// Save progress of labeling data to s3 in_progress
//

// ref: download_all_region_data
function hbc_save_all_region_data(type) {
  // Javascript strings (DOMString) is automatically converted to utf-8
  // see: https://developer.mozilla.org/en-US/docs/Web/API/Blob/Blob
  var all_region_data = pack_via_metadata(type);  // this is [string] of length 1, containing exported labeling data for all images in project panel
  var all_region_data_obj = JSON.parse(all_region_data[0]);
  var curr_img_data = Object.values(all_region_data_obj)[_via_image_index];
  const img_url1 = curr_img_data.filename;
  const file_name = img_url1.replace(/.*\/([^\/]+)$/,'$1');  // remove prefix 'https://s3.amazonaws.com/cerebro-image-annotations/in-progress/'
  const image_id = file_name.replace(/^([0-9]{5}).*/, '$1');   // remove everything except image id
  hbc_put_labeling_data_to_s3(curr_img_data, image_id);
  show_message('Saved progress of file [' + img_url1 + '] to S3.');;
}


function hbc_put_labeling_data_to_s3(data, image_id) {
  const url = `/images/in_progress/${image_id}`;
  fetch(url, {
    method: 'PUT',
    body: JSON.stringify(data),
    headers:{
      'Content-Type': 'application/json'
    }
  }).then(res => res.json())
  .catch(error => console.error('Error:', error))
  .then(function(response) {
    for (var image_id in response) {
      var data = response[image_id];
      var filename = data.filename;
      var size = data.size;
      var img_id1  = _via_get_image_id(filename, size);
      var img_id2  = _via_get_image_id(filename, -1);
      var img_id   = img_id1;

      var regions = data.regions;
      var key, i;
      _via_img_metadata[img_id].regions = [];
      for ( i in regions ) {
        var region_i = new file_region();
        region_i.annotation_id = regions[i].annotation_id
        for ( key in regions[i].shape_attributes ) {
          region_i.shape_attributes[key] = regions[i].shape_attributes[key];
        }
        for ( var key in regions[i].region_attributes ) {
          if ( key === '' ) {
            continue;
          }

          region_i.region_attributes[key] = regions[i].region_attributes[key];

          // add this region attribute to _via_attributes
          if (! key in _via_attributes['region']) {
            _via_attributes['region'][key] = { 'type':'text' };
          }
        }

        // add regions only if they are present
        if ( Object.keys(region_i.shape_attributes).length > 0 ||
             Object.keys(region_i.region_attributes).length > 0 ) {
          _via_img_metadata[img_id].regions.push(region_i);
        }
      }
    }
  });
}
