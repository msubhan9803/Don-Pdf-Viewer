<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  // process the form data here
  $file = $_FILES['file'];
  $summaryContent = $_POST["summaryContent"];
  $curl = curl_init();

  curl_setopt($curl, CURLOPT_URL, 'http://18.142.48.120/upload');
  // curl_setopt($curl, CURLOPT_URL, 'http://127.0.0.1:5000/upload');
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($curl, CURLOPT_POST, true);
  curl_setopt($curl, CURLOPT_POSTFIELDS, array('file' => new \CURLFile($file['tmp_name'], $file['type'], $file['name']), 'summaryContent' => $summaryContent));

  $headers = [
    "Content-Type: multipart/form-data",
  ];
  curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);

  $response = curl_exec($curl);
  curl_close($curl);

  echo $response;
}

// var_dump($data);

?>