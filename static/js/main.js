$DOM = $(document)
$DOM.ready(function(){

    function call_ajax(url, type, data) {
         // this function will perform ajax calls and returns request object

         data = data || '';
         var request = $.ajax({
                             type: type,
                             url: url,
                             data:data,
                       });
         return request;
    }

	function readURL(input){ 
         // this function is used to preview image during creation of post when user uploaded any gif/jpg/png files
         // TODO : the image preview was not clear if image size is big

  	     if (input.files && input.files[0]) {
	    	var reader = new FileReader();
		    reader.onload = function(e) {
		    $('#preview_file').attr('src', e.target.result);
		 }
		 reader.readAsDataURL(input.files[0]);
	  }
    };

    function upload_file(){
        // this function will preview image and enable the post button

    	readURL(this);
        $('#preview_file').removeClass('no_display');
        if(!$('#img_rmve_btn').is(':visible')){
           $('#img_rmve_btn').toggle();
           
        }
        $('#post_feed').removeClass('no_pointer').addClass('pointer').prop('disabled',false);
    }

    function click_file_choose(){
        // this function will open file explorer to select images to upload

        $("#file_upload_ip").click();
    }

    function remove_selected_file(){
       // this function will remove uploaded files by mistake during creation of post

       $('#file_upload_ip').val(null);
       $('#preview_file').addClass('no_display');
       $('#img_rmve_btn').toggle();
    }

    function update_blog(){
       // this function will update the blog description in blog edit page

       blog_id = $(this).parents('.post_card_row').attr('blog_id')
       feed = { 'feed_id': blog_id,
                 'action': 'update',
                 'desc':$('#blog_edit_ip').val(),
              }
	   req = call_ajax('/blogactivity/', 'POST', JSON.stringify(feed));
	   $.when(req).done(function(data) {
		  if(data.success){
			window.location.href = '/'; 
		  }
	   });
    }

    function delete_feed(){
        // this function will delete the feed from the users/admin home page

		obj = $(this);
        blog = $(this).parents('.feed_card');
        feed = { 'feed_id': blog.attr('id'),
                 'action': 'delete'
               }
        url = '/blogactivity/';
		$.confirm({
			title: 'Delete',
			content: 'Are you sure you want to delete post?',
			buttons: {
			  confirm: function() {
				req = call_ajax(url, 'POST', JSON.stringify(feed))
				$.when(req).done(function(data) {
                  if(data.success){
					 blog.remove();
                  }
                });
			  },
			  cancel: function() {},
			},
		});
    }


    function post_feed(){
        // this function will create blog from home page

        event.preventDefault();
        var request = new XMLHttpRequest();
        desc = $('#post_desc').val();
        request.open('POST', '/postfeed/?action=create&desc='+desc, false);
        var formData = new FormData(document.getElementById('file_upload_form'));
        request.send(formData);
        res = request.response;
        if (res == 'OK'){
           window.location.reload();
        }
    }

    function like_unlike_activity(){
        // this function will moniter the activity of like/unlike activity of the blog

        heart_obj = $(this);
        obj = heart_obj.parents('.feed_card');
        feed_id = obj.attr('id');
        feed = {'feed_id':feed_id };
        url = '/blogactivity/';
        
        if($(this).hasClass('fa-heart-o')){
            feed['action'] = 'like';
        }
        else{
            feed['action'] = 'unlike';
        }
        feed_data = JSON.stringify(feed)
        req = call_ajax(url, 'POST', feed_data);
        $.when(req).done(function(data) {
          if(!data.success){
             return 0;
          }
		  if(feed.action == 'like'){
			 heart_obj.removeClass('fa-heart-o').addClass('fa-heart');
		  }
          else{
             heart_obj.removeClass('fa-heart').addClass('fa-heart-o');
          }
		  $('#'+feed_id+' #likes_count').html(data.likes);
        });
        
    }

    function check_blog_desc_length(){
        // this function will enable the blog post button if the length of the blog description 
        // is greater than 0 during creation

        desc = $(this).val();
        $('#letters_count').html(desc.length+' / 130');
        if(desc.length > 0){
          $('#post_feed').removeClass('no_pointer').addClass('pointer').prop('disabled',false);
        }
        else{
          $('#post_feed').removeClass('pointer').addClass('no_pointer').prop('disabled',true);
        }
    }

    function check_comment_length(){
        // this function will enable the reply button for an blog post to comment on it
        // when the comment length is greater than 0

        cmnt = $(this).val();
        blog_id = $(this).parents('.feed_card').attr('id');
        if(cmnt.length > 0){
           $('#' + blog_id + ' #add-comment').removeClass('no_pointer').addClass('pointer').prop('disabled',false);
        }
        else{
           $('#' + blog_id + ' #add-comment').removeClass('pointer').addClass('no_pointer').prop('disabled',true);
        }
    }

    function update_user(){
        // this function will update user firstname, lastname from users setting page

        firstname = $('#id_firstname').val()
        lastname = $('#id_lastname').val()
        req = call_ajax(location.pathname, 'post', 
                  JSON.stringify({'action':'update','firstname':firstname,'lastname':lastname}))
        $.when(req).done(function(data) { 
           if(data.success){
               location.reload()
           }
        }) 
    }

    function change_user_status(){
        // this function will enable/disable the users access to the app
        // this can be done from admins settings page

        user_id = this.name
        _status = this.value
        data = {'action':'change','user_id':user_id, 'status':_status}
        req = call_ajax(location.pathname, 'post', JSON.stringify(data))
        $.when(req).done(function(data) { 
           if(data.success){
               location.reload()
           }
        }) 
    }

    function comment_on_blog(){
        // this function will comment on blog in users/blog page

        blog_id = $(this).parents('.feed_card').attr('id');
        comment = $('#' + blog_id+ ' #comment-ip').val()
        req = call_ajax('/createcomment/', 'post', JSON.stringify({'blog_id':blog_id, 'comment':comment}))
        $.when(req).done(function(data) { 
           if (data.success){
              cmnt_html = `<div class="comment" cmnt_id="` + data.cmnt_id + `">
                                <img src="/static/images/`+ data.avatar +`">
                                <a class="cmnt-user" href="/users/` + data.username + `">` + data.firstname +`</a>
                                <span> `+ comment + `</span>
                           </div>`
              $('#' + blog_id + ' .comment_section').append(cmnt_html)
              cmnts_count = $('#' + blog_id + ' .comment_section .comment').length
              $('#' + blog_id + ' #cmnts_count').html(cmnts_count)
              $('#' + blog_id + ' #comment-ip').val('')
              $('#' + blog_id + ' #add-comment').removeClass('pointer').addClass('no_pointer').prop('disabled',true);
           }
        });
    }

    function copy_blog_link(){
        // this function will copy blog link to clipboard

        blog_id = $(this).parents('.feed_card').attr('id');
        text = location.origin + '/blog/' + blog_id + '/view'
        el = document.createElement('textarea');
		el.value = text;
		document.body.appendChild(el);
		el.select();
		document.execCommand('copy');
		document.body.removeChild(el);
    }

    function bindEvents() {
		$DOM.on('change', '#file_upload_ip', upload_file)
            .on('change', '.form-check-input', change_user_status)
	        .on('click', '.delete_feed', delete_feed)
	        .on('click', '.like_heart', like_unlike_activity)
	        .on('click', '.copy_link', copy_blog_link)
		    .on('click', '#add_image', click_file_choose)
		    .on('click', '#img_rmve_btn', remove_selected_file)
		    .on('click', '#post_feed', post_feed)
	        .on('click', '#add-comment', comment_on_blog)
	        .on('click', '#update_blog', update_blog)
	        .on('click', '#update_user', update_user)
            .on('keyup', '#comment-ip', check_comment_length)
		    .on('input propertychange', "#post_desc", check_blog_desc_length)
    }

    bindEvents();
});
