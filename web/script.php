<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  // process the form data here
  $file = $_FILES['file'];
  $curl = curl_init();

  curl_setopt($curl, CURLOPT_URL, 'http://18.136.213.149/data_processing');
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($curl, CURLOPT_POST, true);
  curl_setopt($curl, CURLOPT_POSTFIELDS, array('file' => new \CURLFile($file['tmp_name'], $file['type'], $file['name'])));

  $headers = [
    "Content-Type: multipart/form-data",
    "x_access_token: xyJ3eXCiOiJKV2QiLCJhbGciOiXIUzI1NiX8"
  ];
  curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);

  $response = curl_exec($curl);
  curl_close($curl);

  echo $response;
}

// var_dump($data);

?>