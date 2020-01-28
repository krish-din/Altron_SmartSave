(function ( doc ) {
  'use strict';
  // Use a more terse method for getting by id
  function getById ( id_string ) {
    return doc.getElementById(id_string);
  }

  function insertAfter( newEl, refEl ) {
    refEl.parentNode.insertBefore(newEl, refEl.nextSibling);
  }

  var editElement = getById('myContent');
  var undoBtn = getById('undo');
  var saveBtn = getById('save');
  var originalContent = editElement.innerHTML;
  var updatedContent = "";

  // if a user has refreshed the page, these declarations
  // will make sure everything is back to square one.
  undoBtn.disabled = true;
  saveBtn.disabled = true;

  // create a redo button
  var redoBtn = doc.createElement('button');
  var redoLabel = doc.createTextNode('Redo');
  redoBtn.id = 'redo';
  redoBtn.className = 'btn';
  redoBtn.hidden = true;
  redoBtn.appendChild(redoLabel);
  insertAfter( redoBtn, undo );

  // if the content has been changed, enable the save button
  editElement.addEventListener('keypress', function () {
    if ( editElement.innerHTML !== originalContent ) {
      saveBtn.disabled = false;
    }
  });

  // on button click, save the updated content
  // to the updatedContent var
  saveBtn.addEventListener('click', function () {
    // updates the myContent block to 'save'
    // the new content to updatedContent var
    updatedContent = getById('myContent').innerHTML;

    if ( updatedContent !== originalContent ) {
      // Show the undo button in the case that you
      // didn't like what you wrote and you want to
      // go back to square one
      undoBtn.disabled = false;
    }
  });

  // If you click the undo button,
  // revert the innerHTML of the contenteditable area to
  // the original statement that was there.
  //
  // Then add in a 'redo' button, to bring back the edited content
  undoBtn.addEventListener('click', function() {
    editElement.innerHTML = originalContent;
    undoBtn.disabled = true;
    redoBtn.hidden = false;
  });

  redoBtn.addEventListener('click', function() {
    editElement.innerHTML = updatedContent;
    this.hidden = true;
    undoBtn.disabled = false;
    undoBtn.focus();
  });

})( document );